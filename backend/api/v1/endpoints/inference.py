import logging
from typing import Optional
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, Response, status
from sqlalchemy.orm import Session

from backend.config import MODEL_NAME, MAX_IMAGE_SIZE_BYTES
from backend.core.ml.model_manager import get_device
from backend.core.ml.inference_engine import run_inference
from backend.core.ml.cam_generator import generate_gradcam
from backend.database.connection import get_db
from backend.repositories.patient_repository import PatientRepository
from backend.services.mappers import patient_to_dict
from backend.schemas import HealthResponse, PredictResponse, AnalyzeResponse, ErrorResponse

logger = logging.getLogger("chest_xray_backend")

router = APIRouter()


@router.get(
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


@router.post(
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


@router.post(
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


@router.post(
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


@router.get("/api/gradcam/{patient_id}/{disease}")
async def dynamic_gradcam_for_disease(patient_id: str, disease: str, db: Session = Depends(get_db)):
    """
    Generate dynamic Grad-CAM heatmap overlay for a specific requested disease on a patient's X-ray.
    """
    patient = PatientRepository.get_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Bemor topilmadi")

    patient_dict = patient_to_dict(patient)
    # Get PROJECT_ROOT by resolving it relative to this file path
    import os
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR)))
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
