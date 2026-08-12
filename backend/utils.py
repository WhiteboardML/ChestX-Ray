import io
import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError
import pydicom

try:
    import pypdfium2 as pdfium
except ImportError:
    pdfium = None


def validate_and_load_image(image_bytes: bytes) -> tuple[np.ndarray, Image.Image]:
    """
    Validate that bytes represent a valid medical or standard image format.
    Supports: JPG, JPEG, PNG, WEBP, BMP, TIF, DICOM (.dcm), PDF (.pdf).

    Returns:
        tuple[np.ndarray, Image.Image]:
            - numpy array of the image (RGB H,W,3 or 2D Grayscale)
            - PIL Image object
    Raises:
        ValueError: If file is empty, corrupted, or unsupported.
    """
    if not image_bytes:
        raise ValueError("Yuklangan fayl bo'sh.")

    # 1. Try DICOM (.dcm) parsing
    if image_bytes.startswith(b'\x00' * 128 + b'DICM') or b'DICM' in image_bytes[:300]:
        try:
            ds = pydicom.dcmread(io.BytesIO(image_bytes))
            arr = ds.pixel_array.astype(float)
            arr -= np.min(arr)
            if np.max(arr) != 0:
                arr = (arr / np.max(arr)) * 255.0
            arr = arr.astype(np.uint8)
            pil_img = Image.fromarray(arr).convert("RGB")
            img_np = np.array(pil_img)
            return img_np, pil_img
        except Exception:
            pass  # Fallback to standard loaders

    # 2. Try PDF (.pdf) rendering
    if image_bytes.startswith(b'%PDF'):
        if pdfium is None:
            raise ValueError("PDF faylini o'qish uchun 'pypdfium2' kutubxonasi o'rnatilishi shart. (pip install pypdfium2)")
        try:
            pdf = pdfium.PdfDocument(image_bytes)
            if len(pdf) == 0:
                raise ValueError("PDF faylida sahifa topilmadi.")
            page = pdf[0]
            pil_img = page.render(scale=2).to_pil().convert("RGB")
            img_np = np.array(pil_img)
            return img_np, pil_img
        except Exception as e:
            raise ValueError(f"PDF faylini o'qishda xatolik yuz berdi: {str(e)}")

    # 3. Standard Image Loading (JPG, JPEG, PNG, WEBP, BMP, TIF)
    try:
        pil_img = Image.open(io.BytesIO(image_bytes))
        pil_img.verify()
        pil_img = Image.open(io.BytesIO(image_bytes))
    except (UnidentifiedImageError, OSError, SyntaxError):
        # Fallback to DICOM
        try:
            ds = pydicom.dcmread(io.BytesIO(image_bytes))
            arr = ds.pixel_array.astype(float)
            arr -= np.min(arr)
            if np.max(arr) != 0:
                arr = (arr / np.max(arr)) * 255.0
            arr = arr.astype(np.uint8)
            pil_img = Image.fromarray(arr).convert("RGB")
            img_np = np.array(pil_img)
        except Exception:
            raise ValueError("Uploaded file is corrupted or not a valid image (Yuklangan fayl shikastlangan yoki rasm formati emas).")

    pil_img = pil_img.convert("RGB")
    img_np = np.array(pil_img)
    if img_np.ndim not in (2, 3):
        raise ValueError("Yaroqsiz rasm o'lchamlari.")

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
