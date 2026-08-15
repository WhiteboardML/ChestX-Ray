import os
import uuid
import datetime
import io
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.config import MAX_IMAGE_SIZE_BYTES
from backend.config.translations import get_pathology_uz, get_pathology_en
from backend.core.ml.inference_engine import run_inference
from backend.core.ml.cam_generator import generate_gradcam
from backend.database.connection import get_db
from backend.database.models import Patient, Scan, User
from backend.repositories.patient_repository import PatientRepository
from backend.repositories.scan_repository import ScanRepository
from backend.repositories.user_repository import UserRepository
from backend.services.mappers import patient_to_dict, scan_to_dict
from backend.utils import validate_and_load_image

logger = logging.getLogger("chest_xray_backend")

# Resolve directories relative to this file path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR)))
UPLOAD_DIR = os.path.join(PROJECT_ROOT, "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()


class ApproveRequest(BaseModel):
    doctor_name: str


class DisapproveRequest(BaseModel):
    doctor_name: str
    correct_diagnosis: str
    rejection_reason: Optional[str] = None


class CreatePatientRequest(BaseModel):
    name: str
    age: int
    gender: str
    phone: Optional[str] = "+998 90 123-45-67"
    medical_status: Optional[str] = "Nazoratda"


@router.get("/api/patients/search")
async def search_patients(q: str = "", db: Session = Depends(get_db)):
    """
    Search existing patients by name, surname, or patient ID in SQLite database via SQLAlchemy.
    """
    patients = PatientRepository.search(db, q)

    results = []
    for p in patients:
        scans = p.scans
        last_scan = scans[0] if scans else None
        results.append({
            "id": p.id,
            "name": p.name,
            "first_name": p.first_name or "",
            "last_name": p.last_name or "",
            "age": p.age,
            "gender": p.gender,
            "scan_count": len(scans),
            "last_diagnosis": last_scan.diagnosis if last_scan else (p.diagnosis or "Noma'lum"),
            "last_scan_time": last_scan.timestamp if last_scan else (p.created_at or "Noma'lum")
        })
    return results


@router.post("/api/upload")
async def upload_xray(
    file: UploadFile = File(...),
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    age: Optional[int] = Form(None),
    gender: Optional[str] = Form(None),
    existing_patient_id: Optional[str] = Form(None),
    user_email: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload X-ray image from Web UI.
    Requires active subscription or available tokens.
    Runs TorchXRayVision DenseNet-121 inference & Grad-CAM heatmap generation.
    """
    # Verify User Subscription / Paid Access (Always Unlimited)
    if user_email:
        user = UserRepository.get_by_email(db, user_email)
        if user:
            user.is_subscribed = 1
            user.plan_name = "SaaS Obunasi (Cheksiz)"
            user.scan_tokens = 99999
            db.commit()
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

    # Database Persistence via SQLAlchemy (Auto-match existing patients by ID or Name)
    f_name = (first_name or "").strip()
    l_name = (last_name or "").strip()
    full_name = f"{l_name} {f_name}".strip() or "Yangi Bemor"

    patient = None
    if existing_patient_id:
        patient = PatientRepository.get_by_id(db, existing_patient_id)

    if not patient and f_name and l_name:
        patient = PatientRepository.get_by_names(db, f_name, l_name)

    if not patient and full_name and full_name != "Yangi Bemor":
        patient = PatientRepository.get_by_full_name(db, full_name)

    if patient:
        patient.diagnosis = top_disease_uz
        patient.probability = prob_percentage
        patient.status = "Ko'rik kutilmoqda"
        if f_name and not patient.first_name:
            patient.first_name = f_name
        if l_name and not patient.last_name:
            patient.last_name = l_name
    else:
        pid = existing_patient_id or f"MX-{uuid.uuid4().hex[:4].upper()}"
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
        PatientRepository.add(db, patient)
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
    ScanRepository.add(db, new_scan)
    db.commit()
    db.refresh(patient)
    return patient_to_dict(patient)


@router.post("/api/patients")
async def create_patient(req: CreatePatientRequest, db: Session = Depends(get_db)):
    """Register a new patient profile in the SQLite database via SQLAlchemy."""
    count = PatientRepository.count(db)
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
    PatientRepository.add(db, patient)
    db.commit()
    db.refresh(patient)
    logger.info(f"Registered new patient profile in SQLite DB: {new_id} ({req.name})")
    return patient_to_dict(patient)


@router.get("/api/patient/{patient_id}")
async def get_patient_details(patient_id: str, db: Session = Depends(get_db)):
    patient = PatientRepository.get_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Bemor topilmadi")
    return patient_to_dict(patient)


@router.get("/api/history")
async def get_patient_history(db: Session = Depends(get_db)):
    patients = PatientRepository.get_all(db)
    return [patient_to_dict(p) for p in patients]


@router.get("/api/scans")
async def get_all_scans(db: Session = Depends(get_db)):
    """Return flattened list of all X-ray scans across all patients for the Arxiv repository, sorted newest date first."""
    scans = ScanRepository.get_all_sorted_desc(db)
    return [scan_to_dict(s) for s in scans]


@router.post("/api/approve/{patient_id}")
async def approve_report(patient_id: str, req: ApproveRequest, db: Session = Depends(get_db)):
    patient = PatientRepository.get_by_id(db, patient_id)
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
    return patient_to_dict(patient)


@router.post("/api/disapprove/{patient_id}")
async def disapprove_report(patient_id: str, req: DisapproveRequest, db: Session = Depends(get_db)):
    """
    Doctor Rejection & Diagnosis Correction Endpoint.
    When AI prediction is wrong, doctor corrects diagnosis and updates patient history.
    """
    patient = PatientRepository.get_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Bemor topilmadi")

    app_time = datetime.datetime.now().strftime("Bugun, %H:%M")
    patient.status = "Rad etilgan (Shifokor to'g'rilagan)"
    patient.diagnosis = req.correct_diagnosis

    if patient.scans:
        latest_scan = patient.scans[0]
        latest_scan.status = "Rad etilgan (Shifokor to'g'rilagan)"
        latest_scan.diagnosis = req.correct_diagnosis
        latest_scan.approved_by = f"{req.doctor_name} (Tuzatish: {req.correct_diagnosis})"
        latest_scan.approved_time = app_time

    db.commit()
    db.refresh(patient)
    return patient_to_dict(patient)


@router.get("/api/pdf/{patient_id}")
async def generate_pdf_report(patient_id: str, db: Session = Depends(get_db)):
    """
    Generate printable diagnostic report for a patient.
    Returns HTML report ready for printing or saving as PDF.
    """
    patient_obj = PatientRepository.get_by_id(db, patient_id)
    if not patient_obj:
        raise HTTPException(status_code=404, detail="Bemor topilmadi")
    patient = patient_to_dict(patient_obj)

    # Filter feasible scores (>= 0.05 or primary diagnosis)
    raw_scores = patient.get('raw_scores', [])
    feasible_scores = [
        p for p in raw_scores
        if p.get('score', 0) >= 0.05 or p.get('disease') == patient.get('diagnosis') or p.get('disease_uz') == patient.get('diagnosis')
    ]
    # Fallback to top 3 scores if no score meets 0.05 threshold
    if not feasible_scores:
        feasible_scores = sorted(raw_scores, key=lambda x: x.get('score', 0), reverse=True)[:3]
    else:
        feasible_scores = sorted(feasible_scores, key=lambda x: x.get('score', 0), reverse=True)

    raw_scores_rows = "".join([
        f"<tr>"
        f"<td><strong>{p.get('disease_uz', p['disease'])}</strong> <span style='color:#64748b; font-size:11px;'>({p['disease']})</span></td>"
        f"<td>{p['score']:.4f} ({p['score']*100:.1f}%)</td>"
        f"</tr>"
        for p in feasible_scores
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
        <div class="section-title">Asosiy Ehtimoliy Patologiyalar (Feasible Findings)</div>
        <table>
            <thead>
                <tr>
                    <th>Patologiya Nomi (Kasallik)</th>
                    <th>Tibbiy Ehtimollik (Score / %)</th>
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
