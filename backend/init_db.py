"""
Database initialization and seed data populator for SQLite.
"""
import logging
from sqlalchemy.orm import Session
from backend.database import engine, Base, SessionLocal
from backend.models import Patient, Scan

logger = logging.getLogger("chest_xray_backend")


def init_db():
    """Create all tables if database is empty."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized cleanly.")



def seed_initial_data(db: Session):
    """Seed sample patients into SQLite database."""
    sample_patients = [
        {
            "id": "MX-8924",
            "first_name": "B. M.",
            "last_name": "Azizov",
            "name": "Azizov B. M.",
            "age": 42,
            "gender": "Erkak",
            "phone": "+998 90 123-45-67",
            "medical_status": "Statsionar",
            "created_at": "2026-08-01",
            "status": "Tasdiqlangan",
            "diagnosis": "Pnevmoniya",
            "probability": 89.0,
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
                    "urgency": {
                        "urgency_code": "CRITICAL",
                        "urgency_badge": "O'ta Shoshilinch 🚨",
                        "urgency_color": "error",
                        "urgency_title": "🚨 O'TA SHOSHILINCH",
                        "action_required": "🚨 Zudlik bilan pulmonolog vrach ko'rigi talab etiladi!"
                    },
                    "raw_scores": [
                        {"disease": "Pneumonia", "disease_uz": "Pnevmoniya", "score": 0.89},
                        {"disease": "Atelectasis", "disease_uz": "Atelektaz", "score": 0.45},
                        {"disease": "Effusion", "disease_uz": "Plevral efuziya", "score": 0.32},
                        {"disease": "Norma", "disease_uz": "Norma (Me'yorda)", "score": 0.11}
                    ],
                    "findings": {
                        "summary": "O'pkaning chap tomonida pnevmoniya (Pneumonia) alomatlari aniqlandi.",
                        "simple_lang": "Bu o'z vaqtida shifokor nazoratida davolansa, asoratsiz tez o'tib ketadigan yallig'lanish.",
                        "precautions": ["Ko'p miqdorda iliq suyuqlik iching.", "Tana haroratini kuzating."],
                        "technical": "TorchXRayVision DenseNet-121 model rentgenogrammada Pneumonia (0.89 score) ko'rsatdi."
                    }
                }
            ]
        },
        {
            "id": "MX-8925",
            "first_name": "F. A.",
            "last_name": "Jumayeva",
            "name": "Jumayeva F. A.",
            "age": 36,
            "gender": "Ayol",
            "phone": "+998 93 456-78-90",
            "medical_status": "Nazoratda",
            "created_at": "2026-08-05",
            "status": "Tasdiqlangan",
            "diagnosis": "Norma",
            "probability": 94.5,
            "scans": [
                {
                    "scan_id": "SCAN-8925-1",
                    "timestamp": "05.08.2026, 09:45",
                    "diagnosis": "Norma",
                    "diagnosis_eng": "Norma",
                    "probability": 94.5,
                    "original_image": "/static/samples/sample_normal.png",
                    "heatmap_image": "/static/samples/sample_normal.png",
                    "status": "Tasdiqlangan",
                    "approved_by": "Dr. A. Karimov",
                    "approved_time": "05.08.2026, 10:15",
                    "urgency": {
                        "urgency_code": "NORMAL",
                        "urgency_badge": "Me'yorda ✅",
                        "urgency_color": "success",
                        "urgency_title": "Me'yorda",
                        "action_required": "✅ Shoshilinchlik holati aniqlanmadi. Bemor sog'lom me'yorda."
                    },
                    "raw_scores": [
                        {"disease": "Norma", "disease_uz": "Norma (Me'yorda)", "score": 0.945},
                        {"disease": "Pneumonia", "disease_uz": "Pnevmoniya", "score": 0.055}
                    ],
                    "findings": {
                        "summary": "O'pka to'qimalari me'yorda. Patologiya aniqlanmadi.",
                        "simple_lang": "Bemor o'pka a'zolari sog'lom va me'yorda.",
                        "precautions": ["Sog'lom turmush tarziga rioya qiling."],
                        "technical": "DenseNet-121 model result: Norma (0.945)."
                    }
                }
            ]
        }
    ]

    for pdata in sample_patients:
        scans_data = pdata.pop("scans", [])
        patient = Patient(**pdata)
        db.add(patient)
        db.flush()

        for sdata in scans_data:
            scan = Scan(patient_id=patient.id, **sdata)
            db.add(scan)

    db.commit()
