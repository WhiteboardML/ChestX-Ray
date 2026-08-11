from backend.model_service import get_model
from tests.test_preprocessing import create_dummy_image_bytes


def test_predict_endpoint_success(client):
    """Test POST /predict accepts image and returns all raw pathology scores in correct order."""
    img_bytes = create_dummy_image_bytes(mode="L", size=(224, 224), fmt="PNG")
    files = {"file": ("test_xray.png", img_bytes, "image/png")}

    response = client.post("/predict", files=files)
    assert response.status_code == 200

    data = response.json()
    assert data["model"] == "densenet121-res224-all"
    assert "predictions" in data

    predictions = data["predictions"]
    model = get_model()

    # Verify count and pathology ordering match model.pathologies exactly
    assert len(predictions) == len(model.pathologies)
    for idx, pred in enumerate(predictions):
        assert pred["disease"] == model.pathologies[idx]
        assert isinstance(pred["score"], float)


def test_analyze_endpoint_success(client):
    """Test POST /analyze accepts image and returns complete structured analysis."""
    img_bytes = create_dummy_image_bytes(mode="RGB", size=(256, 256), fmt="JPEG")
    files = {"file": ("chest_xray.jpg", img_bytes, "image/jpeg")}

    response = client.post("/analyze", files=files)
    assert response.status_code == 200

    data = response.json()
    assert data["model"] == "densenet121-res224-all"
    assert "pathologies" in data

    pathologies = data["pathologies"]
    model = get_model()

    assert len(pathologies) == len(model.pathologies)
    for idx, item in enumerate(pathologies):
        assert item["disease"] == model.pathologies[idx]
        assert isinstance(item["score"], float)


def test_predict_endpoint_invalid_file(client):
    """Test POST /predict with invalid file content returns 400 Bad Request."""
    files = {"file": ("bad.txt", b"Invalid content", "text/plain")}
    response = client.post("/predict", files=files)
    assert response.status_code == 400
    assert "detail" in response.json()
