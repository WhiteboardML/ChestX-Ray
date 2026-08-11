import io
import pytest
import torch
import numpy as np
from PIL import Image

from backend.preprocessing import preprocess_image


def create_dummy_image_bytes(mode: str = "L", size: tuple = (256, 256), fmt: str = "PNG") -> bytes:
    """Helper function to generate synthetic image bytes."""
    if mode == "L":
        arr = np.random.randint(0, 256, size, dtype=np.uint8)
        img = Image.fromarray(arr, mode="L")
    elif mode == "RGB":
        arr = np.random.randint(0, 256, (*size, 3), dtype=np.uint8)
        img = Image.fromarray(arr, mode="RGB")
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


def test_preprocess_valid_grayscale():
    """Test preprocessing valid grayscale image produces correct tensor shape and dtype."""
    img_bytes = create_dummy_image_bytes(mode="L", size=(300, 300), fmt="PNG")
    tensor, orig_gray = preprocess_image(img_bytes, device="cpu")

    assert isinstance(tensor, torch.Tensor)
    assert tensor.shape == (1, 1, 224, 224)
    assert tensor.dtype == torch.float32
    assert isinstance(orig_gray, np.ndarray)
    assert orig_gray.ndim == 2


def test_preprocess_valid_rgb():
    """Test preprocessing valid RGB image handles 3 channels safely."""
    img_bytes = create_dummy_image_bytes(mode="RGB", size=(256, 256), fmt="JPEG")
    tensor, orig_gray = preprocess_image(img_bytes, device="cpu")

    assert isinstance(tensor, torch.Tensor)
    assert tensor.shape == (1, 1, 224, 224)
    assert tensor.dtype == torch.float32
    assert isinstance(orig_gray, np.ndarray)
    assert orig_gray.ndim == 2


def test_preprocess_invalid_image_bytes():
    """Test preprocessing invalid non-image bytes raises ValueError."""
    invalid_bytes = b"Not an image file content"
    with pytest.raises(ValueError, match="corrupted or not a valid image"):
        preprocess_image(invalid_bytes, device="cpu")


def test_preprocess_corrupted_image_bytes():
    """Test preprocessing truncated/corrupted image bytes raises ValueError."""
    img_bytes = create_dummy_image_bytes(mode="L", size=(100, 100), fmt="PNG")
    corrupted_bytes = img_bytes[: len(img_bytes) // 2]
    with pytest.raises(ValueError):
        preprocess_image(corrupted_bytes, device="cpu")
