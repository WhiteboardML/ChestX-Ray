from tests.test_preprocessing import create_dummy_image_bytes


def test_root_and_static_endpoints(client):
    """Test GET / returns index or default HTML message."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Chest X-ray AI Backend Server" in response.text or "html" in response.headers.get("content-type", "")


def test_api_upload_success(client):
    """Test POST /api/upload accepts valid image and returns patient analysis record."""
    img_bytes = create_dummy_image_bytes(mode="L", size=(256, 256), fmt="PNG")
    files = {"file": ("chest_xray.png", img_bytes, "image/png")}

    response = client.post("/api/upload", files=files)
    assert response.status_code == 200

    data = response.json()
    assert "id" in data
    assert data["id"].startswith("MX-")
    assert "diagnosis" in data
    assert "probability" in data
    assert "findings" in data
    assert "raw_scores" in data


def test_api_history_and_details(client):
    """Test GET /api/history and GET /api/patient/{id} return expected data."""
    res_hist = client.get("/api/history")
    assert res_hist.status_code == 200
    patients = res_hist.json()
    assert isinstance(patients, list)
    assert len(patients) >= 2

    # Fetch details for initial patient MX-8924
    res_det = client.get("/api/patient/MX-8924")
    assert res_det.status_code == 200
    det = res_det.json()
    assert det["id"] == "MX-8924"
    assert det["name"] == "Azizov B. M."


def test_api_approve_and_pdf(client):
    """Test POST /api/approve/{id} and GET /api/pdf/{id} endpoints."""
    res_appr = client.post("/api/approve/MX-8924", json={"doctor_name": "Dr. Test Doctor"})
    assert res_appr.status_code == 200
    appr_data = res_appr.json()
    assert appr_data["status"] == "Tasdiqlangan"
    assert appr_data["approved_by"] == "Dr. Test Doctor"

    res_pdf = client.get("/api/pdf/MX-8924")
    assert res_pdf.status_code == 200
    assert "Tibbiy Diagnostika Hisoboti" in res_pdf.text
    assert "MX-8924" in res_pdf.text


def test_api_chat(client):
    """Test POST /api/chat responds with medical advice."""
    res_chat = client.post("/api/chat", json={
        "message": "harorat 39 C isitma bor",
        "diagnosis": "Pnevmoniya",
        "patient_id": "MX-8924"
    })
    assert res_chat.status_code == 200
    data = res_chat.json()
    assert "message" in data
    assert "Paratsetamol" in data["message"] or "harorati" in data["message"]


def test_patient_search_and_multiscan_upload(client):
    """Test GET /api/patients/search and POST /api/upload with existing_patient_id."""
    res_search = client.get("/api/patients/search?q=Azizov")
    assert res_search.status_code == 200
    results = res_search.json()
    assert len(results) >= 1
    assert results[0]["id"] == "MX-8924"

    # Upload new scan for existing patient MX-8924
    img_bytes = create_dummy_image_bytes(mode="L", size=(256, 256), fmt="PNG")
    files = {"file": ("followup_xray.png", img_bytes, "image/png")}
    data = {"existing_patient_id": "MX-8924"}

    res_upload = client.post("/api/upload", files=files, data=data)
    assert res_upload.status_code == 200
    p_data = res_upload.json()
    assert p_data["id"] == "MX-8924"
    assert len(p_data["scans"]) >= 3

