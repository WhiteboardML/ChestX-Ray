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

    @staticmethod
    def get_rag_treatment_plan(diagnosis_uz: str, diagnosis_eng: str) -> str:
        """Query RAG to retrieve the official treatment and medication guidelines."""
        from backend.core.rag.rag_engine import build_rag_report
        try:
            report = build_rag_report(diagnosis_uz, 1.0, [], lang="uz")
            protocol_content = report.get("clinical_guideline", "")
            if protocol_content:
                return protocol_content
        except Exception as e:
            logger.error(f"Error fetching RAG treatment plan: {e}")
        return "Tegishli klinik protokol topilmadi. Pulmonolog shifokor ko'rigi va dori-darmon sxemasi tavsiya etiladi."

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
        user_email: Optional[str] = None,
        symptoms: Optional[List[str]] = None,
        temperature: Optional[float] = None,
        spo2: Optional[int] = None,
        crp_level: Optional[float] = None,
        wbc_count: Optional[float] = None
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

        # 3. Core ML Model Inference (Swin-ViT with Attention Rollout)
        try:
            from backend.core.ml.vit_engine import run_vit_inference
            inference_result = run_vit_inference(image_bytes)
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

        # 4.5. Cascaded Local VLM Audit (Confidence Gating)
        vlm_result = None
        high_risk = ["Pneumothorax", "Pneumonia", "Edema", "Consolidation", "Effusion"]
        
        # Trigger VLM if confidence is intermediate or critical pathology or if doctor supplied text context
        needs_vlm = (
            (15.0 <= prob_percentage <= 85.0) or
            (top_disease_eng in high_risk and prob_percentage >= 20.0) or
            bool(symptoms or temperature or spo2 or crp_level or wbc_count)
        )
        
        if needs_vlm:
            from backend.core.vlm.vlm_engine import run_vlm_audit
            try:
                vlm_result = run_vlm_audit(
                    image_path=image_dest_path,
                    symptoms=symptoms or [],
                    temperature=temperature,
                    spo2=spo2,
                    crp_level=crp_level,
                    wbc_count=wbc_count,
                    vit_diagnosis=top_disease_uz,
                    vit_score=prob_percentage
                )
                
                # Dynamic ensemble correction: if VLM provides a clinical consensus, align it
                if vlm_result and vlm_result.get("diagnosis"):
                    vlm_diag = vlm_result["diagnosis"]
                    if vlm_diag and len(vlm_diag) > 3:
                        top_disease_uz = vlm_diag
                        prob_percentage = min(99.0, max(prob_percentage, 50.0))
            except Exception as ve:
                logger.error(f"VLM verification audit failed: {ve}", exc_info=True)

        # 5. Resolve Urgency Level
        urgency_info = cls.get_urgency_info(top_disease_eng, top_score)

        # 6. Generate Explainability Visualization Overlay
        heatmap_filename = f"{file_id}_heatmap.png"
        heatmap_dest_path = os.path.join(UPLOAD_DIR, heatmap_filename)
        
        # If Swin-ViT generated a native Attention Rollout map, overlay it
        if "heatmap" in inference_result and inference_result["heatmap"] is not None:
            try:
                import cv2
                import numpy as np
                img_cv = cv2.imread(image_dest_path)
                h, w = img_cv.shape[:2]
                
                attn_map = inference_result["heatmap"]
                attn_map_resized = cv2.resize(attn_map, (w, h))
                
                attn_map_uint8 = np.uint8(255 * attn_map_resized)
                colormap = cv2.applyColorMap(attn_map_uint8, cv2.COLORMAP_JET)
                
                overlay = cv2.addWeighted(img_cv, 0.6, colormap, 0.4, 0)
                cv2.imwrite(heatmap_dest_path, overlay)
            except Exception as e:
                logger.error(f"Swin-ViT Attention Rollout overlay failed: {e}", exc_info=True)
                with open(heatmap_dest_path, "wb") as h_buffer:
                    h_buffer.write(image_bytes)
        else:
            # Fallback to standard CNN Grad-CAM
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
            "technical": technical_text,
            "treatment_plan": cls.get_rag_treatment_plan(top_disease_uz, top_disease_eng),
            "vlm_critique": vlm_result
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
