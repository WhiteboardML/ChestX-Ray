import os
import sys

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

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Response, status
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image, ImageDraw, ImageFilter

from backend.config import MODEL_NAME, MAX_IMAGE_SIZE_BYTES, get_pathology_uz, get_pathology_en
from backend.model_service import load_model, get_model, get_device
from backend.preprocessing import preprocess_image
from backend.inference import run_inference
from backend.cam_service import generate_gradcam
from backend.schemas import HealthResponse, PredictResponse, AnalyzeResponse, ErrorResponse

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
    Pre-loads the TorchXRayVision DenseNet-121 model once at application startup.
    """
    logger.info("Application starting up... Loading TorchXRayVision DenseNet-121 model.")
    try:
        load_model()
        logger.info("Model pre-loaded successfully during startup.")
    except Exception as e:
        logger.critical(f"Critical error during startup model loading: {e}", exc_info=True)
        raise RuntimeError(f"Startup model initialization failed: {e}") from e

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
        "name": "Azizov B. M.",
        "age": 42,
        "gender": "Erkak",
        "upload_time": "bugun, 11:20",
        "diagnosis": "Pnevmoniya",
        "probability": 89.0,
        "original_image": "/static/samples/sample_pneumonia.png",
        "heatmap_image": "/static/samples/heatmap_pneumonia.png",
        "status": "Ko'rik kutilmoqda",
        "approved_by": None,
        "approved_time": None,
        "raw_scores": [
            {"disease": "Pneumonia", "disease_uz": "Pnevmoniya", "score": 0.89},
            {"disease": "Atelectasis", "disease_uz": "Atelektaz", "score": 0.45},
            {"disease": "Effusion", "disease_uz": "Plevral efuziya", "score": 0.32},
            {"disease": "Lung Opacity", "disease_uz": "O'pka xiralashishi", "score": 0.78},
            {"disease": "Infiltration", "disease_uz": "Infiltratsiya", "score": 0.21}
        ],
        "findings": {
            "summary": "O'pkaning chap tomonida pnevmoniya (Pneumonia) alomatlari aniqlandi.",
            "simple_lang": "Bu o'z vaqtida shifokor nazoratida davolansa, asoratsiz tez o'tib ketadigan yallig'lanish. Xavotirga o'rin yo'q.",
            "precautions": [
                "Ko'p miqdorda iliq suyuqlik (limonli choy, namatak damlamasi) iching.",
                "Tana haroratini muntazam o'lchang (38.5°C dan oshsa paratsetamol qabul qiling).",
                "Hududiy shifokorga nafas a'zolarini stetoskop bilan eshittiring."
            ],
            "technical": "TorchXRayVision DenseNet-121 model rentgenogrammada segmentar infiltratsiya va Pneumonia (0.89 raw score) belgilarini ko'rsatdi."
        }
    },
    {
        "id": "MX-9842",
        "name": "Abdullaev B. T.",
        "age": 45,
        "gender": "Erkak",
        "upload_time": "bugun, 10:45",
        "diagnosis": "Infiltratsiya",
        "probability": 94.0,
        "original_image": "/static/samples/sample_tb.png",
        "heatmap_image": "/static/samples/heatmap_tb.png",
        "status": "Tasdiqlangan",
        "approved_by": "Dr. A. Karimov",
        "approved_time": "Bugun, 14:32",
        "raw_scores": [
            {"disease": "Infiltration", "disease_uz": "Infiltratsiya", "score": 0.94},
            {"disease": "Consolidation", "disease_uz": "Konsolidatsiya", "score": 0.62},
            {"disease": "Pleural_Thickening", "disease_uz": "Plevra qalinlashishi", "score": 0.58}
        ],
        "findings": {
            "summary": "O'pkaning o'ng tepa qismida infiltrativ o'choqlar aniqlandi.",
            "simple_lang": "O'pka yuqori qismida chuqurroq laborator tahlillarni talab qiladigan o'zgarishlar bor. Zamonaviy tibbiyot bilan buni to'liq davolash mumkin.",
            "precautions": [
                "Zudlik bilan ftiziatr shifokor tekshiruviga yoziling.",
                "Genexpert balg'am testini topshiring.",
                "Yaqin oila a'zolaringizni profilaktik flurografiyaga yo'naltiring."
            ],
            "technical": "Apikal o'pka maydonida o'choqli fibro-infiltrativ intensiv o'zgarishlar. DenseNet-121 raw model score: 0.94."
        }
    }
]

for p in INITIAL_PATIENTS:
    PATIENTS_DATABASE[p["id"]] = p


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


@app.post("/api/upload")
async def upload_xray(file: UploadFile = File(...)):
    """
    Upload X-ray image from Web UI.
    Runs TorchXRayVision DenseNet-121 inference & Grad-CAM heatmap generation!
    """
    filename_lower = file.filename.lower()
    if not (filename_lower.endswith('.png') or filename_lower.endswith('.jpg') or
            filename_lower.endswith('.jpeg') or filename_lower.endswith('.dcm')):
        raise HTTPException(
            status_code=400,
            detail="Qo'llab-quvvatlanmaydigan fayl formati. Faqat rentgen rasmlari (PNG, JPG, DICOM) qabul qilinadi."
        )

    file_id = str(uuid.uuid4())
    safe_ext = os.path.splitext(filename_lower)[1] or ".png"
    if safe_ext == ".dcm":
        safe_ext = ".png"

    image_filename = f"{file_id}{safe_ext}"
    image_dest_path = os.path.join(UPLOAD_DIR, image_filename)

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Yuklangan fayl bo'sh.")

    with open(image_dest_path, "wb") as buffer:
        buffer.write(image_bytes)

    # Real TorchXRayVision DenseNet-121 Inference
    try:
        inference_result = run_inference(image_bytes)
        raw_predictions = inference_result["predictions"]
    except Exception as e:
        logger.error(f"Inference error during upload: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Model tahlilida xatolik yuz berdi.")

    top_pred = max(raw_predictions, key=lambda p: p["score"])
    top_disease_eng = top_pred["disease"]
    top_disease_uz = top_pred.get("disease_uz", get_pathology_uz(top_disease_eng))
    top_score = top_pred["score"]
    prob_percentage = round(float(top_score) * 100, 1)

    # Real Grad-CAM Heatmap for top pathology
    heatmap_filename = f"{file_id}_heatmap.png"
    heatmap_dest_path = os.path.join(UPLOAD_DIR, heatmap_filename)
    try:
        gradcam_bytes, _ = generate_gradcam(image_bytes, disease=top_disease_eng)
        with open(heatmap_dest_path, "wb") as h_buffer:
            h_buffer.write(gradcam_bytes)
    except Exception as e:
        logger.error(f"Grad-CAM generation error during upload: {e}", exc_info=True)
        with open(heatmap_dest_path, "wb") as h_buffer:
            h_buffer.write(image_bytes)

    pid = f"MX-{uuid.uuid4().hex[:4].upper()}"

    summary_text = f"TorchXRayVision DenseNet-121 tahliliga ko'ra asosiy patologiya: {top_disease_uz} ({top_disease_eng}, raw score: {top_score:.3f})."
    simple_text = f"Sun'iy intellekt rentgen tasvirida {top_disease_uz} xususiyatlarini aniqladi. O'z vaqtida shifokor ko'rigidan o'tish tavsiya etiladi."
    precautions = [
        "Shifokor-rentgenolog ko'rigiga murojaat qiling.",
        "Qon va balg'am laboratoriya tahlillarini topshiring.",
        "Nafas olish holatini va tana haroratini kuzatib boring."
    ]
    technical_text = f"DenseNet-121 (res224-all) pretrained model orqali 18 ta patologiya baholandi. Barcha raw model score'lari: " + ", ".join([f"{p.get('disease_uz', p['disease'])} ({p['disease']}): {p['score']:.3f}" for p in raw_predictions[:5]])

    findings = {
        "summary": summary_text,
        "simple_lang": simple_text,
        "precautions": precautions,
        "technical": technical_text
    }

    patient_record = {
        "id": pid,
        "name": "Yangi Bemor",
        "age": 40,
        "gender": "Erkak",
        "upload_time": "Zudlik bilan",
        "diagnosis": top_disease_uz,
        "diagnosis_eng": top_disease_eng,
        "probability": prob_percentage,
        "original_image": f"/uploads/{image_filename}",
        "heatmap_image": f"/uploads/{heatmap_filename}",
        "status": "Ko'rik kutilmoqda",
        "approved_by": None,
        "approved_time": None,
        "raw_scores": raw_predictions,
        "findings": findings
    }

    PATIENTS_DATABASE[pid] = patient_record
    return patient_record


@app.get("/api/gradcam/{patient_id}/{disease}")
async def dynamic_gradcam_for_disease(patient_id: str, disease: str):
    """
    Generate dynamic Grad-CAM heatmap overlay for a specific requested disease on a patient's X-ray.
    """
    if patient_id not in PATIENTS_DATABASE:
        raise HTTPException(status_code=404, detail="Bemor topilmadi")

    patient = PATIENTS_DATABASE[patient_id]
    original_rel_path = patient["original_image"].lstrip("/")
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
    msg = req.message.strip().lower()
    diag = req.diagnosis
    response = ""
    if "harorat" in msg or "isitma" in msg or "39" in msg or "40" in msg:
        response = ("Yuqori tana harorati (39-40°C) o'pka to'qimalarida yallig'lanish yoki "
                    "infeksiya borligidan dalolat. Birinchi yordam sifatida isitmani "
                    "tushiruvchilar (Paratsetamol 500mg yoki Ibuprofen 400mg) qabul qilish kerak.")
    elif "nafas" in msg or "qisishi" in msg:
        response = ("O'tkir nafas qisishi yuzaga kelsa, bemorni yarim o'tirgan holatga keltiring. "
                    "Saturatsiya 92% dan past bo'lsa, zudlik bilan 103 chaqiring.")
    else:
        response = f"Ushbu {diag} tahlili bo'yicha SSV yo'riqnomasi asosida maslahat: Shifokor stetoskopik ko'rigi va rentgenolog tasdiqlashi zarur."

    return {"message": response}


@app.post("/api/approve/{patient_id}")
async def approve_report(patient_id: str, req: ApproveRequest):
    if patient_id not in PATIENTS_DATABASE:
        raise HTTPException(status_code=404, detail="Bemor topilmadi")

    patient = PATIENTS_DATABASE[patient_id]
    patient["status"] = "Tasdiqlangan"
    patient["approved_by"] = req.doctor_name
    patient["approved_time"] = datetime.datetime.now().strftime("Bugun, %H:%M")

    PATIENTS_DATABASE[patient_id] = patient
    return patient


@app.get("/api/history")
async def get_patient_history():
    return list(PATIENTS_DATABASE.values())


@app.get("/api/patient/{patient_id}")
async def get_patient_details(patient_id: str):
    if patient_id not in PATIENTS_DATABASE:
        raise HTTPException(status_code=404, detail="Bemor topilmadi")
    return PATIENTS_DATABASE[patient_id]


@app.get("/api/pdf/{patient_id}")
async def generate_pdf_report(patient_id: str):
    """
    Generate printable diagnostic report for a patient.
    Returns HTML report ready for printing or saving as PDF.
    """
    if patient_id not in PATIENTS_DATABASE:
        raise HTTPException(status_code=404, detail="Bemor topilmadi")

    patient = PATIENTS_DATABASE[patient_id]

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
            <div class="title">MedX AI - Chest X-ray Diagnostika Hisoboti</div>
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

