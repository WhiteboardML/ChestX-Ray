from fastapi import APIRouter
from backend.api.v1.endpoints.inference import router as inference_router
from backend.api.v1.endpoints.patients import router as patients_router
from backend.api.v1.endpoints.assistant import router as assistant_router
from backend.api.v1.endpoints.auth import router as auth_router

api_router = APIRouter()

# Mount all endpoint routers preserving their exact defined API paths
api_router.include_router(inference_router)
api_router.include_router(patients_router)
api_router.include_router(assistant_router)
api_router.include_router(auth_router)
