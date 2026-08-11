def test_health_endpoint(client):
    """Test GET /health returns operational status and model metadata."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["model"] == "densenet121-res224-all"
    assert data["device"] in ("cpu", "cuda")
