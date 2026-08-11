from typing import Tuple, Optional
import logging
import cv2
import numpy as np
import torch
import torch.nn.functional as F
import torchxrayvision as xrv

from backend.model_service import get_model, get_device
from backend.preprocessing import preprocess_image
from backend.utils import encode_array_to_png

logger = logging.getLogger(__name__)


def generate_gradcam(
    image_bytes: bytes,
    disease: Optional[str] = None,
    model: Optional[xrv.models.DenseNet] = None,
    device: Optional[torch.device] = None
) -> Tuple[bytes, str]:
    """
    Generate a Grad-CAM heatmap overlay for a consumer-selected or auto-selected pathology.

    If `disease` is None or empty, automatically selects the pathology with the highest raw prediction score.

    Returns:
        tuple[bytes, str]: (PNG encoded image bytes of Grad-CAM overlay, selected disease name)
    """
    if model is None:
        model = get_model()
    if device is None:
        device = get_device()

    # Preprocess image and get original grayscale image
    tensor, orig_gray = preprocess_image(image_bytes, device=device)
    tensor.requires_grad = True

    activations_list = []
    gradients_list = []

    def forward_hook(module, input_tensor, output_tensor):
        activations_list.append(output_tensor)

    def save_gradient(grad):
        gradients_list.append(grad)

    # Register forward hook on target convolutional feature layer (model.features)
    hook_handle = model.features.register_forward_hook(forward_hook)

    try:
        # Enable gradient computation for Grad-CAM
        with torch.enable_grad():
            output = model(tensor)

            if not disease or not disease.strip():
                # Auto-select pathology with highest prediction score
                target_index = int(torch.argmax(output[0]).item())
                disease = model.pathologies[target_index]
                logger.info(f"Auto-selected highest-scoring pathology '{disease}' for Grad-CAM.")
            else:
                if disease not in model.pathologies:
                    raise ValueError(
                        f"Invalid pathology name '{disease}'. "
                        f"Available pathologies: {model.pathologies}"
                    )
                target_index = model.pathologies.index(disease)

            target_score = output[0, target_index]

            if not activations_list:
                raise RuntimeError("Failed to capture feature activations from model.features.")

            activations = activations_list[0]
            # Register tensor gradient hook
            activations.register_hook(save_gradient)

            # Zero existing gradients and backpropagate from target score
            model.zero_grad()
            target_score.backward()

            if not gradients_list:
                raise RuntimeError("Failed to capture feature gradients during backward pass.")

            gradients = gradients_list[0]

            # 1. Global average pooling of gradients to get channel weights
            weights = gradients.mean(dim=(2, 3), keepdim=True)

            # 2. Weighted linear combination of activation channels
            cam = torch.sum(weights * activations, dim=1, keepdim=True)

            # 3. Apply ReLU to isolate positive contributions
            cam = F.relu(cam)

            # 4. Normalize heatmap to [0, 1] range
            cam_np = cam.detach().cpu().numpy()[0, 0]
            cam_max = cam_np.max()
            cam_min = cam_np.min()

            if cam_max > cam_min:
                cam_normalized = (cam_np - cam_min) / (cam_max - cam_min + 1e-8)
            else:
                cam_normalized = np.zeros_like(cam_np)

            # 5. Resize heatmap to original X-ray image dimensions (H, W)
            orig_h, orig_w = orig_gray.shape[:2]
            heatmap_resized = cv2.resize(
                cam_normalized,
                (orig_w, orig_h),
                interpolation=cv2.INTER_LINEAR
            )

            # 6. Apply color map (JET)
            heatmap_uint8 = np.uint8(255 * heatmap_resized)
            heatmap_bgr = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)

            # 7. Convert original grayscale image to 3-channel BGR
            orig_bgr = cv2.cvtColor(orig_gray, cv2.COLOR_GRAY2BGR)

            # 8. Overlay heatmap onto original X-ray (60% original image + 40% heatmap)
            overlay = cv2.addWeighted(orig_bgr, 0.6, heatmap_bgr, 0.4, 0)

            # 9. Encode overlay image to PNG bytes
            png_bytes = encode_array_to_png(overlay)
            return png_bytes, disease

    except Exception as e:
        logger.error(f"Grad-CAM generation failed for disease '{disease}': {e}", exc_info=True)
        raise
    finally:
        # Crucial: Always remove forward hook to prevent memory leaks and hook accumulation
        hook_handle.remove()

