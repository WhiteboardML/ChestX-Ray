import sys
import logging
from typing import Tuple
import torch
import torchxrayvision as xrv

from backend.config import MODEL_NAME, get_default_device

logger = logging.getLogger(__name__)

# Global model instance and device reference
_model = None
_device = None


def load_model() -> Tuple[xrv.models.DenseNet, torch.device]:
    """
    Load the TorchXRayVision DenseNet-121 (res224-all) model once into memory.
    Configures device (CUDA if available, else CPU) and sets eval mode.
    """
    global _model, _device

    if _model is not None:
        return _model, _device

    # Ensure UTF-8 stdout encoding to handle progress bar characters during weight downloads on Windows
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    _device = get_default_device()
    logger.info(f"Loading TorchXRayVision model '{MODEL_NAME}' on device: {_device}")

    try:
        model = xrv.models.DenseNet(weights=MODEL_NAME)
        model = model.to(_device)
        model.eval()
        _model = model
        logger.info(f"Model '{MODEL_NAME}' successfully loaded and moved to {_device}")
    except Exception as e:
        logger.error(f"Failed to load TorchXRayVision model '{MODEL_NAME}': {e}", exc_info=True)
        raise RuntimeError(f"Could not load TorchXRayVision model '{MODEL_NAME}': {str(e)}") from e

    return _model, _device


def get_model() -> xrv.models.DenseNet:
    """Get loaded model instance. Raises RuntimeError if not loaded."""
    if _model is None:
        raise RuntimeError("Model is not loaded. Call load_model() first.")
    return _model


def get_device() -> torch.device:
    """Get loaded model device. Raises RuntimeError if not loaded."""
    if _device is None:
        raise RuntimeError("Device is not initialized. Call load_model() first.")
    return _device
