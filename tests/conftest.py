import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.model_service import load_model
from backend.database import SessionLocal, engine, Base
from backend.init_db import seed_initial_data


@pytest.fixture(scope="session", autouse=True)
def initialize_model():
    """Pre-load model once for the test session."""
    load_model()


@pytest.fixture(scope="module")
def client():
    """Provide TestClient with isolated seeded test database."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_initial_data(db)
    except Exception:
        pass
    finally:
        db.close()

    with TestClient(app) as test_client:
        yield test_client

    # Reset DB back to empty clean state after test suite runs
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
