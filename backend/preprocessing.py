from typing import Union, Tuple
import cv2
import numpy as np
import torch
import torchxrayvision as xrv

from backend.config import IMAGE_SIZE
from backend.utils import validate_and_load_image


def preprocess_image(
    image_bytes: bytes,
    device: Union[torch.device, str] = "cpu"
) -> Tuple[torch.Tensor, np.ndarray]:
    """
    Preprocess raw image bytes for TorchXRayVision DenseNet-121 inference.

    Steps:
    1. Validate image format and integrity.
    2. Convert RGB to 2D grayscale array safely.
    3. Apply TorchXRayVision intensity normalization (scale to [-1024, 1024]).
    4. Resize to 224x224 model resolution.
    5. Convert to float32 tensor with shape (1, 1, 224, 224).
    6. Move tensor to requested device.

    Args:
        image_bytes (bytes): Raw image file bytes.
        device (torch.device | str): Target PyTorch device.

    Returns:
        tuple[torch.Tensor, np.ndarray]:
            - torch.Tensor: Shape (1, 1, 224, 224) on target device.
            - np.ndarray: Original image as 2D uint8 numpy array (H, W) for overlay.
    """
    img_np, pil_img = validate_and_load_image(image_bytes)

    # Handle grayscale vs RGB safely
    if img_np.ndim == 3:
        if img_np.shape[2] == 4:  # RGBA
            # Convert RGBA to RGB using PIL
            pil_rgb = pil_img.convert("RGB")
            img_np = np.array(pil_rgb)
        
        # Convert RGB to 2D grayscale
        orig_gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    else:
        orig_gray = img_np.copy()

    orig_gray_uint8 = orig_gray.astype(np.uint8)

    # TorchXRayVision normalization expects values scaled to [-1024, 1024]
    # xrv.datasets.normalize accepts numpy array (0 to 255) and max_val=255
    normalized = xrv.datasets.normalize(orig_gray_uint8.astype(np.float32), 255)

    # Resize to model resolution (224, 224)
    resized = cv2.resize(
        normalized,
        (IMAGE_SIZE, IMAGE_SIZE),
        interpolation=cv2.INTER_LINEAR
    )

    # Shape tensor into (1, 1, H, W)
    tensor = torch.from_numpy(resized).float().unsqueeze(0).unsqueeze(0)

    # Move to target device
    tensor = tensor.to(device)

    return tensor, orig_gray_uint8
