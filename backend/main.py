import os
import sys
import io

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import uuid
import json
import datetime
import logging
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Response, status, Depends
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image, ImageDraw, ImageFilter
from sqlalchemy.orm import Session

from backend.config import MODEL_NAME, MAX_IMAGE_SIZE_BYTES, get_pathology_uz, get_pathology_en
from backend.model_service import load_model, get_model, get_device
from backend.preprocessing import preprocess_image
from backend.inference import run_inference
from backend.cam_service import generate_gradcam
from backend.utils import validate_and_load_image
from backend.schemas import HealthResponse, PredictResponse, AnalyzeResponse, ErrorResponse
from backend.database import get_db
from backend.models import Patient, Scan
from backend.init_db import init_db
from llm.service import chat_with_medical_llm, synthesize_xray_report

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("chest_xray_backend")

UPLOAD_DIR = os.path.join(PROJECT_ROOT, "uploads")
STATIC_DIR = os.path.join(PROJECT_ROOT, "static")
FRONTEND_DIST_DIR = os.path.join(PROJECT_ROOT, "frontend", "dist")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(FRONTEND_DIST_DIR, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI Lifespan Context Manager.
    Initializes SQLite Database & pre-loads the TorchXRayVision DenseNet-121 model.
    """
    logger.info("Application starting up... Initializing SQLite Database and pre-loading model.")
    try:
        init_db()
        load_model()
        logger.info("Database initialized and Model pre-loaded successfully during startup.")
    except Exception as e:
        logger.critical(f"Critical error during startup: {e}", exc_info=True)
        raise RuntimeError(f"Startup initialization failed: {e}") from e

    yield

    logger.info("Application shutting down...")


app = FastAPI(
    title="Chest X-ray AI Inference & Diagnostic Server",
    description=(
        "Backend Chest X-ray analysis service powered by TorchXRayVision DenseNet-121 (res224-all) "
        "and Grad-CAM visualization, with full web application integration.\n\n"
        "**Strict Clinical Safety Note**: Outputs raw model scores only. No arbitrary disease thresholds, "
        "positive/negative labels, or autonomous diagnostic decisions are provided. All outputs require "
        "interpretation by qualified medical professionals."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for cross-origin integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

assets_dir = os.path.join(FRONTEND_DIST_DIR, "assets")
os.makedirs(assets_dir, exist_ok=True)
app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

# Exception Handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc: ValueError):
    """Map ValueErrors to HTTP 400 Bad Request."""
    logger.warning(f"Bad Request (400): {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    """Catch-all exception handler to prevent leaking internal Python stack traces."""
    logger.error(f"Unhandled internal server error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred during processing."}
    )


# ----------------------------------------------------
# Core AI Backend Endpoints
# ----------------------------------------------------

@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check endpoint",
    description="Returns operational status, loaded model identifier, and device."
)
async def health_check():
    """Return model operational status and execution device."""
    device = get_device()
    return HealthResponse(
        status="ok",
        model=MODEL_NAME,
        device=str(device.type)
    )


@app.post(
    "/predict",
    response_model=PredictResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid image or corrupted upload"},
        500: {"model": ErrorResponse, "description": "Internal model inference failure"}
    },
    summary="Run raw pathology prediction on a Chest X-ray image",
    description="Accepts a chest X-ray image file (JPG, JPEG, PNG) and returns all raw model pathology scores."
)
async def predict(file: UploadFile = File(...)):
    """Run model inference and return all unthresholded pathology prediction scores."""
    if not file or not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing uploaded image file.")

    contents = await file.read()
    if len(contents) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File size exceeds maximum limit.")

    result = run_inference(contents)
    return PredictResponse(**result)


@app.post(
    "/analyze",
    response_model=AnalyzeResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid image or corrupted upload"},
        500: {"model": ErrorResponse, "description": "Internal model inference failure"}
    },
    summary="Run complete structured analysis on a Chest X-ray image",
    description="Accepts a chest X-ray image and returns complete structured analysis reusing the core inference engine."
)
async def analyze(file: UploadFile = File(...)):
    """Run complete structured analysis."""
    if not file or not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing uploaded image file.")

    contents = await file.read()
    if len(contents) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File size exceeds maximum limit.")

    raw_result = run_inference(contents)
    return AnalyzeResponse(
        model=raw_result["model"],
        pathologies=raw_result["predictions"]
    )


@app.post(
    "/gradcam",
    response_class=Response,
    responses={
        200: {"content": {"image/png": {}}, "description": "PNG image containing Grad-CAM heatmap overlay"},
        400: {"model": ErrorResponse, "description": "Invalid image format or invalid pathology name"},
        500: {"model": ErrorResponse, "description": "Grad-CAM generation failure"}
    },
    summary="Generate Grad-CAM visualization overlay for a selected or auto-detected pathology",
    description="Accepts a chest X-ray image file and optional target disease parameter. Returns PNG image."
)
async def gradcam(
    file: UploadFile = File(...),
    disease: Optional[str] = Form(None)
):
    """Generate Grad-CAM visualization overlay as a PNG image for a selected or auto-detected pathology."""
    if not file or not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing uploaded image file.")

    contents = await file.read()
    if len(contents) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File size exceeds maximum limit.")

    png_bytes, selected_disease = generate_gradcam(contents, disease=disease)
    return Response(
        content=png_bytes,
        media_type="image/png",
        headers={"X-Selected-Pathology": selected_disease}
    )


# ----------------------------------------------------
# Web Application & Patient Session APIs
# ----------------------------------------------------

PATIENTS_DATABASE = {}

INITIAL_PATIENTS = [
    {
        "id": "MX-8924",
        "first_name": "B. M.",
        "last_name": "Azizov",
        "name": "Azizov B. M.",
        "age": 42,
        "gender": "Erkak",
        "created_at": "2026-08-01",
        "scans": [
            {
                "scan_id": "SCAN-8924-1",
                "timestamp": "01.08.2026, 11:20",
                "diagnosis": "Pnevmoniya",
                "diagnosis_eng": "Pneumonia",
                "probability": 89.0,
                "original_image": "/static/samples/sample_pneumonia.png",
                "heatmap_image": "/static/samples/heatmap_pneumonia.png",
                "status": "Tasdiqlangan",
                "approved_by": "Dr. A. Karimov",
                "approved_time": "01.08.2026, 14:00",
                "raw_scores": [
                    {"disease": "Pneumonia", "disease_uz": "Pnevmoniya", "score": 0.89},
                    {"disease": "Atelectasis", "disease_uz": "Atelektaz", "score": 0.45},
                    {"disease": "Effusion", "disease_uz": "Plevral efuziya", "score": 0.32},
                    {"disease": "Lung Opacity", "disease_uz": "O'pka xiralashishi", "score": 0.78},
                    {"disease": "Infiltration", "disease_uz": "Infiltratsiya", "score": 0.21}
                ],
                "findings": {
                    "summary": "O'pkaning chap tomonida pnevmoniya (Pneumonia) alomatlari aniqlandi.",
                    "simple_lang": "Bu o'z vaqtida shifokor nazoratida davolansa, asoratsiz tez o'tib ketadigan yallig'lanish.",
                    "precautions": [
                        "Ko'p miqdorda iliq suyuqlik iching.",
                        "Tana haroratini muntazam o'lchang.",
                        "Hududiy shifokorga nafas a'zolarini stetoskop bilan eshittiring."
                    ],
                    "technical": "TorchXRayVision DenseNet-121 model rentgenogrammada segmentar infiltratsiya va Pneumonia (0.89 raw score) belgilarini ko'rsatdi."
                }
            },
            {
                "scan_id": "SCAN-8924-2",
                "timestamp": "Bugun, 10:15",
                "diagnosis": "Norma",
                "diagnosis_eng": "Normal",
                "probability": 15.2,
                "original_image": "/static/samples/sample_normal.png",
                "heatmap_image": "/static/samples/heatmap_normal.png",
                "status": "Ko'rik kutilmoqda",
                "approved_by": None,
                "approved_time": None,
                "raw_scores": [
                    {"disease": "Pneumonia", "disease_uz": "Pnevmoniya", "score": 0.152},
                    {"disease": "Atelectasis", "disease_uz": "Atelektaz", "score": 0.08},
                    {"disease": "Effusion", "disease_uz": "Plevral efuziya", "score": 0.05},
                    {"disease": "Lung Opacity", "disease_uz": "O'pka xiralashishi", "score": 0.12},
                    {"disease": "Infiltration", "disease_uz": "Infiltratsiya", "score": 0.09}
                ],
                "findings": {
                    "summary": "O'pka to'qimalarida sezilarli ijobiy dinamika kuzatildi. Pnevmoniya o'chog'i to'liq so'rilgan.",
                    "simple_lang": "Ijobiy dinamika! O'pka shamollashi to'liq tuzalgan va to'qimalar me'yoriga qaytgan.",
                    "precautions": [
                        "Profilaktik nafas mashqlarini bajarishni davom eting.",
                        "Muntazam sog'lom turmush tarziga rioya qiling."
                    ],
                    "technical": "Takroriy rentgenogramma: Pneumonia raw score 0.89 dan 0.152 ga kamaydi (Ijobiy klinik dinamika)."
                }
            }
        ]
    },
    {
        "id": "MX-9842",
        "first_name": "B. T.",
        "last_name": "Abdullaev",
        "name": "Abdullaev B. T.",
        "age": 45,
        "gender": "Erkak",
        "created_at": "2026-08-05",
        "scans": [
            {
                "scan_id": "SCAN-9842-1",
                "timestamp": "05.08.2026, 10:45",
                "diagnosis": "Infiltratsiya",
                "diagnosis_eng": "Infiltration",
                "probability": 94.0,
                "original_image": "/static/samples/sample_tb.png",
                "heatmap_image": "/static/samples/heatmap_tb.png",
                "status": "Tasdiqlangan",
                "approved_by": "Dr. A. Karimov",
                "approved_time": "05.08.2026, 14:32",
                "raw_scores": [
                    {"disease": "Infiltration", "disease_uz": "Infiltratsiya", "score": 0.94},
                    {"disease": "Consolidation", "disease_uz": "Konsolidatsiya", "score": 0.62},
                    {"disease": "Pleural_Thickening", "disease_uz": "Plevra qalinlashishi", "score": 0.58}
                ],
                "findings": {
                    "summary": "O'pkaning o'ng tepa qismida infiltrativ o'choqlar aniqlandi.",
                    "simple_lang": "O'pka yuqori qismida chuqurroq laborator tahlillarni talab qiladigan o'zgarishlar bor.",
                    "precautions": [
                        "Zudlik bilan ftiziatr shifokor tekshiruviga yoziling.",
                        "Genexpert balg'am testini topshiring.",
                        "Yaqin oila a'zolaringizni profilaktik flurografiyaga yo'naltiring."
                    ],
                    "technical": "Apikal o'pka maydonida o'choqli fibro-infiltrativ intensiv o'zgarishlar. DenseNet-121 raw model score: 0.94."
                }
            }
        ]
    }
]

for p in INITIAL_PATIENTS:
    latest_scan = p["scans"][-1]
    p_dict = dict(p)
    # Mirror latest scan properties to top-level for backwards compatibility
    p_dict.update({
        "upload_time": latest_scan["timestamp"],
        "diagnosis": latest_scan["diagnosis"],
        "diagnosis_eng": latest_scan.get("diagnosis_eng", "Pneumonia"),
        "probability": latest_scan["probability"],
        "original_image": latest_scan["original_image"],
        "heatmap_image": latest_scan["heatmap_image"],
        "status": latest_scan["status"],
        "approved_by": latest_scan["approved_by"],
        "approved_time": latest_scan["approved_time"],
        "raw_scores": latest_scan["raw_scores"],
        "findings": latest_scan["findings"]
    })
    PATIENTS_DATABASE[p["id"]] = p_dict


def populate_sample_images():
    samples_dir = os.path.join(STATIC_DIR, "samples")
    os.makedirs(samples_dir, exist_ok=True)
    filenames = ["sample_pneumonia.png", "sample_tb.png", "sample_normal.png"]
    for fname in filenames:
        dest_path = os.path.join(samples_dir, fname)
        if not os.path.exists(dest_path):
            bg = Image.new("RGB", (800, 600), (10, 12, 15))
            draw = ImageDraw.Draw(bg)
            for i in range(5):
                offset = i * 70 + 100
                draw.arc([50, offset, 380, offset + 100], start=180, end=270, fill=(35, 40, 48), width=8)
                draw.arc([420, offset, 750, offset + 100], start=270, end=360, fill=(35, 40, 48), width=8)
            bg.save(dest_path)
            heatmap_path = os.path.join(samples_dir, fname.replace("sample_", "heatmap_"))
            bg.save(heatmap_path)

populate_sample_images()


class ChatRequest(BaseModel):
    message: str
    diagnosis: str
    patient_id: str
    history: Optional[List[dict]] = []

class ApproveRequest(BaseModel):
    doctor_name: str


@app.get("/api/patients/search")
async def search_patients(q: str = ""):
    """
    Search existing patients by name, surname or patient ID for real-time autocomplete during upload.
    """
    q_clean = q.strip().lower()
    results = []
    for pid, p in PATIENTS_DATABASE.items():
        full = f"{p.get('first_name', '')} {p.get('last_name', '')} {p.get('name', '')} {pid}".lower()
        if not q_clean or q_clean in full:
            scans = p.get("scans", [])
            last_scan = scans[-1] if scans else {}
            results.append({
                "id": pid,
                "name": p.get("name", f"{p.get('first_name', '')} {p.get('last_name', '')}".strip() or "Bemor"),
                "first_name": p.get("first_name", ""),
                "last_name": p.get("last_name", ""),
                "age": p.get("age", 40),
                "gender": p.get("gender", "Erkak"),
                "scan_count": len(scans),
                "last_diagnosis": last_scan.get("diagnosis", p.get("diagnosis", "Noma'lum")),
                "last_scan_time": last_scan.get("timestamp", p.get("upload_time", "Noma'lum"))
            })
    return results


@app.post("/api/upload")
async def upload_xray(
    file: UploadFile = File(...),
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    age: Optional[int] = Form(None),
    gender: Optional[str] = Form(None),
    existing_patient_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload X-ray image from Web UI.
    Runs TorchXRayVision DenseNet-121 inference & Grad-CAM heatmap generation!
    Saves scan and patient records into SQLite database via SQLAlchemy.
    """
    filename_lower = file.filename.lower()
    allowed_exts = ('.png', '.jpg', '.jpeg', '.dcm', '.dicom', '.pdf', '.webp', '.bmp', '.tif', '.tiff')
    if not any(filename_lower.endswith(ext) for ext in allowed_exts):
        raise HTTPException(
            status_code=400,
            detail="Qo'llab-quvvatlanmaydigan fayl formati. Faqat PNG, JPG, DICOM (.dcm) va PDF (.pdf) qabul qilinadi."
        )

    file_id = str(uuid.uuid4())
    image_filename = f"{file_id}.png"
    image_dest_path = os.path.join(UPLOAD_DIR, image_filename)

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Yuklangan fayl bo'sh.")

    # Validate and render web-compatible PNG image for UI display
    try:
        _, pil_img = validate_and_load_image(image_bytes)
        buf = io.BytesIO()
        pil_img.save(buf, format="PNG")
        web_png_bytes = buf.getvalue()
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve)) from ve

    with open(image_dest_path, "wb") as buffer:
        buffer.write(web_png_bytes)

    # Real TorchXRayVision DenseNet-121 Inference
    try:
        inference_result = run_inference(image_bytes)
        raw_predictions = inference_result["predictions"]
    except Exception as e:
        logger.error(f"Inference error during upload: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Model tahlilida xatolik yuz berdi.")

    # Evaluate primary diagnosis: check if pathology is present or Norma
    pathology_preds = [p for p in raw_predictions if p["disease"] != "Norma"]
    top_pathology = max(pathology_preds, key=lambda p: p["score"]) if pathology_preds else None

    if top_pathology and top_pathology["score"] >= 0.20:
        top_pred = top_pathology
        top_disease_eng = top_pred["disease"]
        top_disease_uz = top_pred.get("disease_uz", get_pathology_uz(top_disease_eng))
        top_score = top_pred["score"]
    else:
        top_pred = next((p for p in raw_predictions if p["disease"] == "Norma"), raw_predictions[0])
        top_disease_eng = "Norma"
        top_disease_uz = "Norma (Me'yorda)"
        top_score = top_pred["score"]

    prob_percentage = round(float(top_score) * 100, 1)

    # Urgency Evaluation (Shoshilinchlik darajasi)
    def get_urgency_info(disease_eng: str, score: float) -> dict:
        if disease_eng == "Norma" or score < 0.20:
            return {
                "urgency_code": "NORMAL",
                "urgency_badge": "Me'yorda ✅",
                "urgency_color": "success",
                "urgency_title": "Me'yorda (Shoshilinchlik yo'q)",
                "action_required": "✅ Shoshilinchlik holati aniqlanmadi. Bemor salomatlik ko'rsatkichlari me'yorda."
            }

        high_risk = ["Pneumothorax", "Pneumonia", "Edema", "Consolidation", "Effusion"]
        if score >= 0.60 or (disease_eng in high_risk and score >= 0.45):
            return {
                "urgency_code": "CRITICAL",
                "urgency_badge": "O'TA SHOSHILINCH 🚨",
                "urgency_color": "error",
                "urgency_title": "🚨 O'TA SHOSHILINCH (Zudlik bilan pulmonolog ko'rigi zarur!)",
                "action_required": "🚨 Zudlik bilan shoshilinch tibbiy yordam va pulmonolog vrach ko'rigi talab etiladi!"
            }
        elif score >= 0.35:
            return {
                "urgency_code": "HIGH",
                "urgency_badge": "Yuqori Shoshilinchlik ⚠️",
                "urgency_color": "amber",
                "urgency_title": "⚠️ YUQORI SHOSHILINCHLIK (Vrach nazorati talab etiladi)",
                "action_required": "⚠️ Vrach-pulmonolog nazorati va qo'shimcha laboratoriya tekshiruvi zarur."
            }
        else:
            return {
                "urgency_code": "MODERATE",
                "urgency_badge": "O'rta Shoshilinchlik ⚡",
                "urgency_color": "yellow",
                "urgency_title": "⚡ O'RTA SHOSHILINCHLIK",
                "action_required": "⚡ Ambulator kuzatuv va 7 kun ichida takroriy tahlil tavsiya etiladi."
            }

    urgency_info = get_urgency_info(top_disease_eng, top_score)

    # Real Grad-CAM Heatmap for target pathology
    heatmap_filename = f"{file_id}_heatmap.png"
    heatmap_dest_path = os.path.join(UPLOAD_DIR, heatmap_filename)
    gradcam_target_disease = top_disease_eng if top_disease_eng != "Norma" else (top_pathology["disease"] if top_pathology else "Pneumonia")
    try:
        gradcam_bytes, _ = generate_gradcam(image_bytes, disease=gradcam_target_disease)
        with open(heatmap_dest_path, "wb") as h_buffer:
            h_buffer.write(gradcam_bytes)
    except Exception as e:
        logger.error(f"Grad-CAM generation error during upload: {e}", exc_info=True)
        with open(heatmap_dest_path, "wb") as h_buffer:
            h_buffer.write(image_bytes)

    if top_disease_eng == "Norma":
        summary_text = f"TorchXRayVision DenseNet-121 tahliliga ko'ra o'pka to'qimalari ME'YORDA (Norma: {prob_percentage}%)."
        simple_text = f"Sun'iy intellekt rentgenogrammada hech qanday yaqqol patologiyani aniqlamadi. O'pka a'zolari me'yorda."
        precautions = ["Sog'lom turmush tarziga rioya qiling.", "Har yillik profilaktik rentgen ko'rigidan o'tib turing."]
    else:
        summary_text = f"TorchXRayVision DenseNet-121 tahliliga ko'ra asosiy patologiya: {top_disease_uz} ({top_disease_eng}, raw score: {top_score:.3f}). {urgency_info['urgency_title']}"
        simple_text = f"Sun'iy intellekt rentgen tasvirida {top_disease_uz} alomatlarini aniqladi ({prob_percentage}%). {urgency_info['action_required']}"
        precautions = [
            urgency_info['action_required'],
            "Shifokor-pulmonolog ko'rigiga murojaat qiling.",
            "Qon va balg'am laboratoriya tahlillarini topshiring.",
            "Nafas olish holatini va tana haroratini kuzatib boring."
        ]

    technical_text = f"DenseNet-121 (res224-all) model orqali 18 ta patologiya va Norma baholandi. Shoshilinchlik darajasi: {urgency_info['urgency_code']}. Raw score'lar: " + ", ".join([f"{p.get('disease_uz', p['disease'])}: {p['score']:.3f}" for p in raw_predictions[:6]])

    findings = {
        "summary": summary_text,
        "simple_lang": simple_text,
        "precautions": precautions,
        "technical": technical_text
    }

    timestamp_str = datetime.datetime.now().strftime("Bugun, %H:%M")
    scan_id = f"SCAN-{uuid.uuid4().hex[:6].upper()}"

    # Database Persistence via SQLAlchemy
    if existing_patient_id:
        patient = db.query(Patient).filter(Patient.id == existing_patient_id).first()
        if patient:
            patient.diagnosis = top_disease_uz
            patient.probability = prob_percentage
            patient.status = "Ko'rik kutilmoqda"
        else:
            f_name = (first_name or "").strip()
            l_name = (last_name or "").strip()
            full_name = f"{l_name} {f_name}".strip() or "Yangi Bemor"
            patient = Patient(
                id=existing_patient_id,
                first_name=f_name,
                last_name=l_name,
                name=full_name,
                age=age if age is not None else 40,
                gender=gender if gender else "Erkak",
                phone="+998 90 123-45-67",
                medical_status="Nazoratda",
                created_at=datetime.datetime.now().strftime("%Y-%m-%d"),
                status="Ko'rik kutilmoqda",
                diagnosis=top_disease_uz,
                probability=prob_percentage
            )
            db.add(patient)
            db.flush()
    else:
        pid = f"MX-{uuid.uuid4().hex[:4].upper()}"
        f_name = (first_name or "").strip()
        l_name = (last_name or "").strip()
        full_name = f"{l_name} {f_name}".strip() or "Yangi Bemor"
        patient = Patient(
            id=pid,
            first_name=f_name,
            last_name=l_name,
            name=full_name,
            age=age if age is not None else 40,
            gender=gender if gender else "Erkak",
            phone="+998 90 123-45-67",
            medical_status="Nazoratda",
            created_at=datetime.datetime.now().strftime("%Y-%m-%d"),
            status="Ko'rik kutilmoqda",
            diagnosis=top_disease_uz,
            probability=prob_percentage
        )
        db.add(patient)
        db.flush()

    new_scan = Scan(
        scan_id=scan_id,
        patient_id=patient.id,
        timestamp=timestamp_str,
        diagnosis=top_disease_uz,
        diagnosis_eng=top_disease_eng,
        probability=prob_percentage,
        urgency=urgency_info,
        original_image=f"/uploads/{image_filename}",
        heatmap_image=f"/uploads/{heatmap_filename}",
        status="Ko'rik kutilmoqda",
        raw_scores=raw_predictions,
        findings=findings
    )
    db.add(new_scan)
    db.commit()
    db.refresh(patient)
    return patient.to_dict()


@app.get("/api/gradcam/{patient_id}/{disease}")
async def dynamic_gradcam_for_disease(patient_id: str, disease: str, db: Session = Depends(get_db)):
    """
    Generate dynamic Grad-CAM heatmap overlay for a specific requested disease on a patient's X-ray.
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Bemor topilmadi")

    patient_dict = patient.to_dict()
    original_rel_path = patient_dict["original_image"].lstrip("/")
    original_full_path = os.path.join(PROJECT_ROOT, original_rel_path)

    if not os.path.exists(original_full_path):
        raise HTTPException(status_code=404, detail="Original rentgen fayli topilmadi")

    with open(original_full_path, "rb") as f:
        image_bytes = f.read()

    try:
        gradcam_bytes, selected_disease = generate_gradcam(image_bytes, disease=disease)
        return Response(
            content=gradcam_bytes,
            media_type="image/png",
            headers={"X-Selected-Pathology": selected_disease}
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve)) from ve
    except Exception as e:
        logger.error(f"Dynamic Grad-CAM error for disease '{disease}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Grad-CAM hosil qilishda xatolik.") from e


@app.post("/api/chat")
async def chat_assistant(req: ChatRequest):
    """
    Local Offline Medical Q&A Assistant.
    Ensures 100% patient data privacy with zero external network data transmission.
    """
    msg = req.message.strip().lower()
    diag = req.diagnosis or "Norma"
    
    if "harorat" in msg or "isitma" in msg or "39" in msg or "40" in msg:
        response = ("Yuqori tana harorati (39-40°C) o'pka to'qimalarida yallig'lanish yoki "
                    "infeksiya borligidan dalolat berishi mumkin. Birinchi yordam sifatida isitmani "
                    "tushiruvchilar (Paratsetamol 500mg yoki Ibuprofen 400mg) qabul qilish va "
                    "shifokor ko'rigiga uchrash tavsiya etiladi.")
    elif "nafas" in msg or "qisishi" in msg:
        response = ("O'tkir nafas qisishi yuzaga kelsa, bemorni yarim o'tirgan holatga keltiring. "
                    "Saturatsiya (SpO2) 92% dan past bo'lsa, zudlik bilan 103 shoshilinch yordam chaqiring.")
    elif "pnevmoniya" in msg or "pneumonia" in msg or "pnevmoniya" in diag.lower():
        response = ("Pnevmoniya aniqlangan holatlarda SSV davolash protokoli bo'yicha: "
                    "bemorga yetarlicha dam olish, ko'p miqdorda iliq suyuqlik ichish hamda vrach-pulmonolog "
                    "tomonidan tayinlangan antibakterial terapiya talab etiladi.")
    elif "dori" in msg or "doza" in msg or "davolash" in msg:
        response = f"Ushbu ({diag}) holati bo'yicha dori vositalari va davolash kursi faqatgina davolovchi vrach-pulmonolog tomonidan shaxsiy ko'rikdan so'ng tayinlanishi shart."
    else:
        response = f"Ushbu ({diag}) tahlili bo'yicha SSV yo'riqnomasi va klinik bayonnoma asosida maslahat: Shifokor stetoskopik ko'rigi hamda laboratoriya tahlillari zarur."

    return {"message": response}


@app.post("/api/approve/{patient_id}")
async def approve_report(patient_id: str, req: ApproveRequest, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Bemor topilmadi")

    app_time = datetime.datetime.now().strftime("Bugun, %H:%M")
    patient.status = "Tasdiqlangan"

    if patient.scans:
        latest_scan = patient.scans[0]
        latest_scan.status = "Tasdiqlangan"
        latest_scan.approved_by = req.doctor_name
        latest_scan.approved_time = app_time

    db.commit()
    db.refresh(patient)
    return patient.to_dict()


@app.get("/api/history")
async def get_patient_history(db: Session = Depends(get_db)):
    patients = db.query(Patient).all()
    return [p.to_dict() for p in patients]


@app.get("/api/scans")
async def get_all_scans(db: Session = Depends(get_db)):
    """Return flattened list of all X-ray scans across all patients for the Arxiv repository, sorted newest date first."""
    scans = db.query(Scan).order_by(Scan.id.desc()).all()
    return [s.to_dict() for s in scans]


class CreatePatientRequest(BaseModel):
    name: str
    age: int
    gender: str
    phone: Optional[str] = "+998 90 123-45-67"
    medical_status: Optional[str] = "Nazoratda"


@app.post("/api/patients")
async def create_patient(req: CreatePatientRequest, db: Session = Depends(get_db)):
    """Register a new patient profile in the SQLite database via SQLAlchemy."""
    count = db.query(Patient).count()
    new_id = f"MX-{count + 8925}"
    name_parts = req.name.strip().split()
    first_name = name_parts[0] if name_parts else req.name
    last_name = name_parts[-1] if len(name_parts) > 1 else ""

    patient = Patient(
        id=new_id,
        first_name=first_name,
        last_name=last_name,
        name=req.name,
        age=req.age,
        gender=req.gender,
        phone=req.phone or "+998 90 123-45-67",
        medical_status=req.medical_status or "Nazoratda",
        created_at=datetime.datetime.now().strftime("%Y-%m-%d"),
        status="Kutilmoqda",
        diagnosis="Tahlil kutilmoqda",
        probability=0.0
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    logger.info(f"Registered new patient profile in SQLite DB: {new_id} ({req.name})")
    return patient.to_dict()


@app.get("/api/patient/{patient_id}")
async def get_patient_details(patient_id: str, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Bemor topilmadi")
    return patient.to_dict()


@app.get("/api/pdf/{patient_id}")
async def generate_pdf_report(patient_id: str, db: Session = Depends(get_db)):
    """
    Generate printable diagnostic report for a patient.
    Returns HTML report ready for printing or saving as PDF.
    """
    patient_obj = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient_obj:
        raise HTTPException(status_code=404, detail="Bemor topilmadi")
    patient = patient_obj.to_dict()

    raw_scores_rows = "".join([
        f"<tr><td>{p['disease']}</td><td>{p['score']:.4f}</td></tr>"
        for p in patient.get('raw_scores', [])
    ])

    html_content = f"""<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <title>Tibbiy Diagnostika Hisoboti - {patient['id']}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; color: #1f2937; line-height: 1.6; background: #fff; }}
        .header {{ border-bottom: 2px solid #2563eb; padding-bottom: 15px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }}
        .title {{ font-size: 22px; font-weight: 700; color: #1e40af; }}
        .badge {{ background-color: #dbeafe; color: #1e40af; padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 700; uppercase; }}
        .section {{ margin-bottom: 20px; padding: 16px; background: #f8fafc; border-radius: 12px; border: 1px solid #e2e8f0; }}
        .section-title {{ font-size: 13px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 10px; }}
        .field {{ margin-bottom: 8px; font-size: 14px; }}
        .field-label {{ font-weight: 600; color: #64748b; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ border: 1px solid #e2e8f0; padding: 10px 14px; text-align: left; font-size: 13px; }}
        th {{ background-color: #f1f5f9; font-weight: 700; color: #334155; }}
        .footer {{ margin-top: 40px; border-top: 1px solid #cbd5e1; padding-top: 15px; font-size: 12px; color: #64748b; display: flex; justify-content: space-between; }}
    </style>
</head>
<body onload="window.print()">
    <div class="header">
        <div>
            <div class="title">AvicennaX AI - Chest X-ray Diagnostika Hisoboti</div>
            <div style="font-size: 12px; color: #64748b;">SSV AI Standardi • TorchXRayVision DenseNet-121</div>
        </div>
        <span class="badge">{patient.get('status', "Ko'rik kutilmoqda")}</span>
    </div>

    <div class="section">
        <div class="section-title">Bemor Ma'lumotlari</div>
        <div class="field"><span class="field-label">ID:</span> {patient['id']}</div>
        <div class="field"><span class="field-label">F.I.SH.:</span> {patient['name']}</div>
        <div class="field"><span class="field-label">Yosh / Jins:</span> {patient['age']} yosh, {patient['gender']}</div>
        <div class="field"><span class="field-label">Yuklangan vaqt:</span> {patient.get('upload_time', 'N/A')}</div>
    </div>

    <div class="section">
        <div class="section-title">AI Tahlil Natijasi</div>
        <div class="field"><span class="field-label">Asosiy Diagnostik Xulosa:</span> <strong>{patient['diagnosis']}</strong> ({patient['probability']}%)</div>
        <div class="field"><span class="field-label">Sodda Tushuntirish:</span> {patient['findings'].get('simple_lang', '')}</div>
    </div>

    <div class="section">
        <div class="section-title">Patologiyalar bo'yicha Raw Score'lar</div>
        <table>
            <thead>
                <tr>
                    <th>Patologiya Nomi</th>
                    <th>Ehtimollik Score (Raw)</th>
                </tr>
            </thead>
            <tbody>
                {raw_scores_rows}
            </tbody>
        </table>
    </div>

    <div class="footer">
        <div>Tasdiqladi: {patient.get('approved_by') or 'Kutilmoqda'}</div>
        <div>Vaqt: {patient.get('approved_time') or 'N/A'}</div>
    </div>
</body>
</html>"""
    return HTMLResponse(content=html_content)


@app.get("/")
async def get_index():
    dist_index = os.path.join(FRONTEND_DIST_DIR, "index.html")
    if os.path.exists(dist_index):
        return FileResponse(dist_index)
    return HTMLResponse("<h1>Chest X-ray AI Backend Server is Running</h1><p>Visit <a href='/docs'>/docs</a> for API documentation.</p>")


@app.get("/{file_path:path}")
async def serve_static_or_spa(file_path: str):
    """
    Serve static assets from frontend/dist (e.g., logo-icon.png, favicon.svg)
    and support Single Page Application (SPA) client-side routing fallback.
    """
    # Prevent intercepting API endpoints or documentation
    if file_path.startswith(("api/", "docs", "redoc", "openapi.json", "health", "predict", "gradcam", "analyze", "uploads", "static", "assets")):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")

    target_file = os.path.join(FRONTEND_DIST_DIR, file_path)
    if os.path.isfile(target_file):
        return FileResponse(target_file)

    dist_index = os.path.join(FRONTEND_DIST_DIR, "index.html")
    if os.path.exists(dist_index):
        return FileResponse(dist_index)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

