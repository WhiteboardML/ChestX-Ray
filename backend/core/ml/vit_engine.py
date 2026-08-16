import torch
import torch.nn as nn
import numpy as np
import logging
from PIL import Image
import io
from typing import Dict, Any, List, Tuple
from transformers import AutoImageProcessor, ViTForImageClassification
from backend.config.translations import get_pathology_uz, get_pathology_ru
from backend.core.ml.model_manager import get_model, get_device
from backend.core.ml.preprocessor import preprocess_image
from backend.core.ml.inference_engine import run_inference

logger = logging.getLogger("chest_xray_backend")

# Global singleton for ViT
_vit_model = None
_vit_processor = None

def get_vit_model_and_processor():
    """
    Load pre-trained NIH Chest X-ray ViT model and processor.
    Falls back to None if offline or if memory allocation fails.
    """
    global _vit_model, _vit_processor
    if _vit_model is not None:
        return _vit_model, _vit_processor

    logger.info("Initializing pre-trained NIH Chest X-ray ViT model...")
    try:
        model_name = "Sohaibsoussi/ViT-NIH-Chest-X-ray-dataset-small"
        _vit_processor = AutoImageProcessor.from_pretrained(model_name)
        _vit_model = ViTForImageClassification.from_pretrained(model_name)
        
        device = get_device()
        _vit_model.to(device)
        _vit_model.eval()
        logger.info("NIH Chest X-ray ViT model initialized successfully.")
        return _vit_model, _vit_processor
    except Exception as e:
        logger.warning(f"Failed to load pre-trained ViT, using CNN baseline fallback: {e}")
        _vit_model = None
        _vit_processor = None
        return None, None

def compute_attention_rollout(attentions: Tuple[torch.Tensor, ...]) -> np.ndarray:
    """
    Perform Attention Rollout algorithm across ViT self-attention weights.
    Returns a normalized 2D heatmap.
    """
    # Average attention across all heads per layer
    mean_attentions = []
    for attn in attentions:
        attn_averaged = attn.mean(dim=1).squeeze(0)  # (seq_len, seq_len)
        mean_attentions.append(attn_averaged)

    seq_len = mean_attentions[0].size(-1)
    rollout = torch.eye(seq_len, device=mean_attentions[0].device)
    for attn in mean_attentions:
        attn_res = 0.5 * attn + 0.5 * torch.eye(seq_len, device=attn.device)
        rollout = torch.matmul(attn_res, rollout)

    # Standard ViT models use a CLS (classification) token at index 0.
    # The impact of the 196 patches on the CLS token is located at rollout[0, 1:]
    if seq_len == 197:  # 14x14 patches + 1 CLS token
        attn_map = rollout[0, 1:].detach().cpu().numpy()
        grid_size = 14
    else:
        # Fallback for other layouts
        attn_map = rollout.mean(dim=0).detach().cpu().numpy()
        grid_size = int(np.sqrt(seq_len))
        if grid_size * grid_size != seq_len:
            grid_size = 7
        if len(attn_map) > grid_size * grid_size:
            attn_map = attn_map[:grid_size * grid_size]

    heatmap = attn_map.reshape((grid_size, grid_size))
    
    # Normalize
    heatmap = (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min() + 1e-8)
    return heatmap

def run_vit_inference(image_bytes: bytes) -> Dict[str, Any]:
    """
    Run pre-trained NIH ViT model inference and extract Attention Rollout heatmap.
    Falls back to DenseNet CNN inference if ViT is unavailable.
    """
    model, processor = get_vit_model_and_processor()
    if model is None:
        logger.info("NIH ViT model not loaded. Falling back to DenseNet CNN inference...")
        return run_inference(image_bytes)

    device = get_device()
    try:
        # Load image via PIL
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        inputs = processor(images=image, return_tensors="pt").to(device)

        # Run forward pass, requesting self-attention maps
        with torch.no_grad():
            outputs = model(**inputs, output_attentions=True)
            logits = outputs.logits
            attentions = outputs.attentions  # Tuple of (batch, heads, seq, seq) tensors

        # Map predictions using model labels
        probs = torch.softmax(logits, dim=-1)[0].detach().cpu().numpy()
        
        predictions = []
        max_score = 0.0
        
        for idx in range(len(probs)):
            disease_raw = model.config.id2label.get(idx, f"Pathology_{idx}")
            # Map 'No Finding' to 'Norma'
            disease = "Norma" if disease_raw == "No Finding" else disease_raw
            score = float(probs[idx])
            
            # Track maximum score for other pathologies to derive Norma if needed
            if disease != "Norma" and score > max_score:
                max_score = score
                
            predictions.append({
                "disease": disease,
                "disease_uz": get_pathology_uz(disease),
                "disease_ru": get_pathology_ru(disease),
                "score": score
            })

        # Generate Attention Rollout heatmap
        heatmap = None
        if attentions:
            try:
                heatmap = compute_attention_rollout(attentions)
            except Exception as he:
                logger.error(f"Error computing attention rollout: {he}")

        return {
            "model": "ViT-NIH-Chest-Xray",
            "predictions": predictions,
            "heatmap": heatmap
        }
    except Exception as e:
        logger.error(f"ViT inference failed: {e}. Falling back to CNN...", exc_info=True)
        return run_inference(image_bytes)
