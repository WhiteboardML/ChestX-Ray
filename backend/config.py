import os
import torch

MODEL_NAME = "densenet121-res224-all"
IMAGE_SIZE = 224
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

def get_default_device() -> torch.device:
    """Return CUDA device if available, otherwise CPU."""
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")
