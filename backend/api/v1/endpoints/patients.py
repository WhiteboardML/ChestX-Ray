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

from backend.services.inference_orchestrator import InferenceOrchestrator
from backend.services.report_generator import ReportGenerator
from backend.database.connection import get_db
from backend.database.models import Patient, Scan, User
from backend.repositories.patient_repository import PatientRepository
from backend.repositories.scan_repository import ScanRepository
from backend.repositories.user_repository import UserRepository
from backend.services.mappers import patient_to_dict, scan_to_dict

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
    symptoms: Optional[str] = Form(None),
    temperature: Optional[float] = Form(None),
    spo2: Optional[int] = Form(None),
    crp_level: Optional[float] = Form(None),
    wbc_count: Optional[float] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload X-ray image from Web UI.
    Requires active subscription or available tokens.
    Runs TorchXRayVision DenseNet-121 / Swin-ViT inference & Qwen2-VL verification.
    """
    filename_lower = file.filename.lower()
    allowed_exts = ('.png', '.jpg', '.jpeg', '.dcm', '.dicom', '.pdf', '.webp', '.bmp', '.tif', '.tiff')
    if not any(filename_lower.endswith(ext) for ext in allowed_exts):
        raise HTTPException(
            status_code=400,
            detail="Qo'llab-quvvatlanmaydigan fayl formati. Faqat PNG, JPG, DICOM (.dcm) va PDF (.pdf) qabul qilinadi."
        )

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Yuklangan fayl bo'sh.")

    symptoms_list = []
    if symptoms:
        try:
            import json
            parsed = json.loads(symptoms)
            if isinstance(parsed, list):
                symptoms_list = [str(item) for item in parsed]
            else:
                symptoms_list = [str(parsed)]
        except Exception:
            symptoms_list = [s.strip() for s in symptoms.split(",") if s.strip()]

    try:
        patient_dict = InferenceOrchestrator.process_xray(
            db=db,
            image_bytes=image_bytes,
            first_name=first_name,
            last_name=last_name,
            age=age,
            gender=gender,
            existing_patient_id=existing_patient_id,
            user_email=user_email,
            symptoms=symptoms_list,
            temperature=temperature,
            spo2=spo2,
            crp_level=crp_level,
            wbc_count=wbc_count
        )
        return patient_dict
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve)) from ve
    except Exception as e:
        logger.error(f"Upload and analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Tahlil jarayonida xatolik yuz berdi.") from e


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

    html_content = ReportGenerator.compile_html_report(patient)
    return HTMLResponse(content=html_content)


@router.get("/api/stats/dashboard")
async def get_dashboard_statistics(db: Session = Depends(get_db)):
    """
    Get aggregated dashboard statistics for clinical diagnostics visualization.
    """
    scans = ScanRepository.get_all_sorted_desc(db)
    patients_count = PatientRepository.count(db)
    
    total_scans = len(scans)
    
    # Aggregators
    pathologies = {}
    urgency_distribution = {"CRITICAL": 0, "HIGH": 0, "MODERATE": 0, "NORMAL": 0}
    approval_stats = {"Tasdiqlangan": 0, "Rad etilgan": 0, "Ko'rik kutilmoqda": 0}
    
    for s in scans:
        # Pathology count
        path = s.diagnosis_eng or "Norma"
        pathologies[path] = pathologies.get(path, 0) + 1
        
        # Urgency count
        urg_code = "NORMAL"
        if s.urgency and isinstance(s.urgency, dict):
            urg_code = s.urgency.get("urgency_code", "NORMAL")
        urgency_distribution[urg_code] = urgency_distribution.get(urg_code, 0) + 1
        
        # Approval status count
        app_status = s.status or "Ko'rik kutilmoqda"
        if "Rad etilgan" in app_status:
            approval_stats["Rad etilgan"] += 1
        elif "Tasdiqlangan" in app_status:
            approval_stats["Tasdiqlangan"] += 1
        else:
            approval_stats["Ko'rik kutilmoqda"] += 1

    return {
        "total_scans": total_scans,
        "total_patients": patients_count,
        "pathology_distribution": pathologies,
        "urgency_distribution": urgency_distribution,
        "approval_stats": approval_stats
    }

