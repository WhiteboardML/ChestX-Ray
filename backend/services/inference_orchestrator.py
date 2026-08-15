import os
import uuid
import datetime
import io
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from backend.config import MAX_IMAGE_SIZE_BYTES
from backend.config.translations import get_pathology_uz, get_pathology_en
from backend.core.ml.inference_engine import run_inference
from backend.core.ml.cam_generator import generate_gradcam
from backend.database.models import Patient, Scan, User
from backend.repositories.patient_repository import PatientRepository
from backend.repositories.scan_repository import ScanRepository
from backend.repositories.user_repository import UserRepository
from backend.services.mappers import patient_to_dict
from backend.utils import validate_and_load_image

logger = logging.getLogger("chest_xray_backend")

# Resolve directories relative to this file path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))
UPLOAD_DIR = os.path.join(PROJECT_ROOT, "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)


class InferenceOrchestrator:
    """
    Service Orchestrator that manages the pipeline for chest X-ray uploads:
    image validation -> inference -> primary diagnosis resolution -> urgency analysis -> Grad-CAM overlay -> DB persistence.
    """

    @staticmethod
    def get_urgency_info(disease_eng: str, score: float) -> Dict[str, Any]:
        """Evaluate clinical urgency status and recommended immediate actions."""
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

    @classmethod
    def process_xray(
        cls,
        db: Session,
        image_bytes: bytes,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        age: Optional[int] = None,
        gender: Optional[str] = None,
        existing_patient_id: Optional[str] = None,
        user_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process uploaded chest X-ray bytes, run ML and Grad-CAM, match or register a patient,
        save a scan record, and return the serialized patient object.
        """
        # 1. Update/Verify User Subscription Settings
        if user_email:
            user = UserRepository.get_by_email(db, user_email)
            if user:
                user.is_subscribed = 1
                user.plan_name = "SaaS Obunasi (Cheksiz)"
                user.scan_tokens = 99999
                db.commit()

        # 2. Validate Image and generate web-compatible PNG bytes
        try:
            _, pil_img = validate_and_load_image(image_bytes)
            buf = io.BytesIO()
            pil_img.save(buf, format="PNG")
            web_png_bytes = buf.getvalue()
        except ValueError as ve:
            raise ValueError(str(ve)) from ve

        file_id = str(uuid.uuid4())
        image_filename = f"{file_id}.png"
        image_dest_path = os.path.join(UPLOAD_DIR, image_filename)

        with open(image_dest_path, "wb") as buffer:
            buffer.write(web_png_bytes)

        # 3. Core ML Model Inference
        try:
            inference_result = run_inference(image_bytes)
            raw_predictions = inference_result["predictions"]
        except Exception as e:
            logger.error(f"Inference error in orchestrator: {e}", exc_info=True)
            raise RuntimeError("Model tahlilida xatolik yuz berdi.") from e

        # 4. Resolve Primary Diagnosis
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

        # 5. Resolve Urgency Level
        urgency_info = cls.get_urgency_info(top_disease_eng, top_score)

        # 6. Generate Grad-CAM visualization overlay
        heatmap_filename = f"{file_id}_heatmap.png"
        heatmap_dest_path = os.path.join(UPLOAD_DIR, heatmap_filename)
        gradcam_target_disease = top_disease_eng if top_disease_eng != "Norma" else (top_pathology["disease"] if top_pathology else "Pneumonia")
        try:
            gradcam_bytes, _ = generate_gradcam(image_bytes, disease=gradcam_target_disease)
            with open(heatmap_dest_path, "wb") as h_buffer:
                h_buffer.write(gradcam_bytes)
        except Exception as e:
            logger.error(f"Grad-CAM generation error in orchestrator: {e}", exc_info=True)
            with open(heatmap_dest_path, "wb") as h_buffer:
                h_buffer.write(image_bytes)

        # 7. Compile Narrative Findings & Recommendations
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

        # 8. Resolve or Register Patient Identity in SQLite DB
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

        # 9. Register Scan Record
        timestamp_str = datetime.datetime.now().strftime("Bugun, %H:%M")
        scan_id = f"SCAN-{uuid.uuid4().hex[:6].upper()}"

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
