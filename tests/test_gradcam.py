import io
from PIL import Image
from backend.model_service import get_model
from tests.test_preprocessing import create_dummy_image_bytes


def test_gradcam_endpoint_valid_pathology(client):
    """Test POST /gradcam with valid pathology returns PNG overlay image."""
    img_bytes = create_dummy_image_bytes(mode="L", size=(300, 300), fmt="PNG")
    files = {"file": ("chest.png", img_bytes, "image/png")}
    data = {"disease": "Pneumonia"}

    response = client.post("/gradcam", files=files, data=data)
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.headers["x-selected-pathology"] == "Pneumonia"

    # Verify PNG image can be opened by PIL
    cam_img = Image.open(io.BytesIO(response.content))
    assert cam_img.format == "PNG"
    assert cam_img.size == (300, 300)


def test_gradcam_endpoint_auto_select_pathology(client):
    """Test POST /gradcam without providing disease parameter auto-selects highest scoring pathology."""
    img_bytes = create_dummy_image_bytes(mode="L", size=(250, 250), fmt="PNG")
    files = {"file": ("chest.png", img_bytes, "image/png")}

    # Omit 'disease' parameter
    response = client.post("/gradcam", files=files)
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert "x-selected-pathology" in response.headers
    assert len(response.headers["x-selected-pathology"]) > 0

    cam_img = Image.open(io.BytesIO(response.content))
    assert cam_img.format == "PNG"
    assert cam_img.size == (250, 250)



def test_gradcam_endpoint_invalid_pathology(client):
    """Test POST /gradcam with invalid pathology returns 400 Bad Request."""
    img_bytes = create_dummy_image_bytes(mode="L", size=(224, 224), fmt="PNG")
    files = {"file": ("chest.png", img_bytes, "image/png")}
    data = {"disease": "NonExistentDisease"}

    response = client.post("/gradcam", files=files, data=data)
    assert response.status_code == 400
    assert "Invalid pathology" in response.json()["detail"]


def test_gradcam_repeated_calls_no_hook_leak(client):
    """Test repeated Grad-CAM requests do not accumulate forward or backward hooks."""
    model = get_model()
    initial_fwd_hooks = len(model.features._forward_hooks)

    img_bytes = create_dummy_image_bytes(mode="L", size=(200, 200), fmt="PNG")

    for disease_name in ["Pneumonia", "Atelectasis", "Effusion"]:
        files = {"file": ("chest.png", img_bytes, "image/png")}
        data = {"disease": disease_name}
        res = client.post("/gradcam", files=files, data=data)
        assert res.status_code == 200

    # Ensure hook count has not grown
    current_fwd_hooks = len(model.features._forward_hooks)
    assert current_fwd_hooks == initial_fwd_hooks
