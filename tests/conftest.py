import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.model_service import load_model


@pytest.fixture(scope="session", autouse=True)
def initialize_model():
    """Pre-load model once for the test session."""
    load_model()


@pytest.fixture(scope="module")
def client():
    """Provide TestClient with lifespan events active."""
    with TestClient(app) as test_client:
        yield test_client
