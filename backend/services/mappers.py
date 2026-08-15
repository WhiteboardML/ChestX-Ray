import datetime
from backend.database.models import Patient, Scan, User


def user_to_dict(user: User) -> dict:
    """Convert User database model to dictionary format."""
    if not user:
        return {}
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "role": user.role,
        "is_subscribed": bool(user.is_subscribed),
        "plan_name": user.plan_name,
        "scan_tokens": user.scan_tokens,
        "card_number": user.card_number,
        "created_at": user.created_at
    }


def scan_to_dict(scan: Scan) -> dict:
    """Convert Scan database model to dictionary format."""
    if not scan:
        return {}
    return {
        "id": scan.id,
        "scan_id": scan.scan_id,
        "patient_id": scan.patient_id,
        "patient_name": scan.patient.name if scan.patient else "",
        "patient_age": scan.patient.age if scan.patient else 0,
        "patient_gender": scan.patient.gender if scan.patient else "",
        "patient_phone": scan.patient.phone if scan.patient else "+998 90 123-45-67",
        "timestamp": scan.timestamp,
        "diagnosis": scan.diagnosis,
        "diagnosis_eng": scan.diagnosis_eng,
        "probability": scan.probability,
        "urgency": scan.urgency,
        "original_image": scan.original_image,
        "heatmap_image": scan.heatmap_image,
        "status": scan.status,
        "approved_by": scan.approved_by,
        "approved_time": scan.approved_time,
        "raw_scores": scan.raw_scores,
        "findings": scan.findings
    }


def patient_to_dict(patient: Patient) -> dict:
    """Convert Patient database model to dictionary format."""
    if not patient:
        return {}
    scans_list = [scan_to_dict(scan) for scan in patient.scans] if patient.scans else []
    latest_scan = patient.scans[0] if patient.scans else None

    return {
        "id": patient.id,
        "first_name": patient.first_name or "",
        "last_name": patient.last_name or "",
        "name": patient.name,
        "age": patient.age,
        "gender": patient.gender,
        "phone": patient.phone or "+998 90 123-45-67",
        "medical_status": patient.medical_status or "Nazoratda",
        "created_at": patient.created_at or datetime.datetime.now().strftime("%Y-%m-%d"),
        "status": patient.status or "Kutilmoqda",
        "diagnosis": patient.diagnosis or "Norma",
        "probability": patient.probability or 0.0,
        "upload_time": latest_scan.timestamp if latest_scan else patient.created_at,
        "original_image": latest_scan.original_image if latest_scan else None,
        "heatmap_image": latest_scan.heatmap_image if latest_scan else None,
        "approved_by": patient.status == "Tasdiqlangan" and (latest_scan.approved_by if latest_scan else None) or None,
        "approved_time": latest_scan.approved_time if latest_scan else None,
        "raw_scores": latest_scan.raw_scores if latest_scan else [],
        "findings": latest_scan.findings if latest_scan else {
            "summary": "Bemor profil yaratildi.",
            "simple_lang": "Rentgen tahlilini o'tkazish uchun yangi fayl yuklang.",
            "precautions": ["Bemor holatini kuzatib boring."],
            "technical": "Profile created."
        },
        "urgency": latest_scan.urgency if latest_scan else None,
        "scans": scans_list
    }
