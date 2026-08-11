import io
import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError


def validate_and_load_image(image_bytes: bytes) -> tuple[np.ndarray, Image.Image]:
    """
    Validate that bytes represent a valid image (JPG, JPEG, PNG).
    Handles grayscale and RGB safely.

    Returns:
        tuple[np.ndarray, Image.Image]:
            - numpy array of the image (grayscale H,W or RGB H,W,3)
            - PIL Image object
    Raises:
        ValueError: If file is empty, corrupted, or unsupported.
    """
    if not image_bytes:
        raise ValueError("Uploaded file is empty.")

    try:
        pil_img = Image.open(io.BytesIO(image_bytes))
        pil_img.verify()  # Verify that image is not corrupted
        
        # Re-open after verify as per PIL documentation
        pil_img = Image.open(io.BytesIO(image_bytes))
    except (UnidentifiedImageError, OSError, SyntaxError) as e:
        raise ValueError(f"Uploaded file is corrupted or not a valid image: {str(e)}")

    valid_formats = {"JPEG", "JPG", "PNG"}
    if pil_img.format and pil_img.format.upper() not in valid_formats:
        raise ValueError(
            f"Unsupported image format: '{pil_img.format}'. "
            f"Supported formats are JPG, JPEG, PNG."
        )

    # Convert PIL Image to numpy array
    img_np = np.array(pil_img)
    if img_np.ndim not in (2, 3):
        raise ValueError("Invalid image dimensions. Image must be 2D grayscale or 3D RGB.")

    return img_np, pil_img


def encode_array_to_png(img_bgr: np.ndarray) -> bytes:
    """
    Encode a BGR numpy array to PNG bytes.

    Args:
        img_bgr (np.ndarray): BGR image array (uint8)

    Returns:
        bytes: PNG encoded bytes
    """
    success, encoded = cv2.imencode(".png", img_bgr)
    if not success:
        raise RuntimeError("Failed to encode Grad-CAM image to PNG format.")
    return encoded.tobytes()
