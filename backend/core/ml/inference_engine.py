from typing import List, Dict, Any
import torch
import torchxrayvision as xrv

from backend.config import MODEL_NAME
from backend.config.translations import get_pathology_uz, get_pathology_ru
from backend.core.ml.model_manager import get_model, get_device
from backend.core.ml.preprocessor import preprocess_image


def run_inference(
    image_bytes: bytes,
    model: xrv.models.DenseNet = None,
    device: torch.device = None
) -> Dict[str, Any]:
    """
    Run TorchXRayVision DenseNet-121 inference on raw chest X-ray image bytes.

    Returns raw pathology scores without applying thresholds or classification labels.

    Args:
        image_bytes (bytes): Uploaded chest X-ray file bytes.
        model (xrv.models.DenseNet, optional): Model instance (defaults to loaded singleton).
        device (torch.device, optional): Target device (defaults to loaded singleton device).

    Returns:
        Dict[str, Any]: Structured dictionary with 'model' name and 'predictions' list.
    """
    if model is None:
        model = get_model()
    if device is None:
        device = get_device()

    # Preprocess image into float tensor (1, 1, 224, 224)
    tensor, _ = preprocess_image(image_bytes, device=device)

    # Perform inference with gradients disabled
    with torch.no_grad():
        outputs = model(tensor)

    # Extract 1D predictions tensor (18 scores)
    scores = outputs[0].detach().cpu().numpy()

    # Map raw scores dynamically to model.pathologies
    predictions: List[Dict[str, Any]] = []
    max_pathology_score = 0.0

    for pathology_name, score_val in zip(model.pathologies, scores):
        eng_name = str(pathology_name)
        val = float(score_val)
        if val > max_pathology_score:
            max_pathology_score = val
        predictions.append({
            "disease": eng_name,
            "disease_uz": get_pathology_uz(eng_name),
            "disease_ru": get_pathology_ru(eng_name),
            "score": val
        })

    # Add explicit Norma (Normal / No Pathology) category
    norma_score = max(0.0, min(1.0, 1.0 - max_pathology_score))
    predictions.append({
        "disease": "Norma",
        "disease_uz": get_pathology_uz("Norma"),
        "disease_ru": get_pathology_ru("Norma"),
        "score": float(norma_score)
    })

    return {
        "model": MODEL_NAME,
        "predictions": predictions
    }
