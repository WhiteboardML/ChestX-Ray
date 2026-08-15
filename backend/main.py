import os
import sys
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Adjust Python path to allow root level imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.core.ml.model_manager import load_model
from backend.init_db import init_db
from backend.api.v1.router import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("chest_xray_backend")

UPLOAD_DIR = os.path.join(PROJECT_ROOT, "uploads")
STATIC_DIR = os.path.join(PROJECT_ROOT, "static")
FRONTEND_DIST_DIR = os.path.join(PROJECT_ROOT, "frontend", "dist")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(FRONTEND_DIST_DIR, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI Lifespan Context Manager.
    Initializes SQLite Database & pre-loads the TorchXRayVision DenseNet-121 model.
    """
    logger.info("Application starting up... Initializing SQLite Database and pre-loading model.")
    try:
        init_db()
        load_model()
        logger.info("Database initialized and Model pre-loaded successfully during startup.")
    except Exception as e:
        logger.critical(f"Critical error during startup: {e}", exc_info=True)
        raise RuntimeError(f"Startup initialization failed: {e}") from e

    yield

    logger.info("Application shutting down...")


app = FastAPI(
    title="Chest X-ray AI Inference & Diagnostic Server",
    description=(
        "Backend Chest X-ray analysis service powered by TorchXRayVision DenseNet-121 (res224-all) "
        "and Grad-CAM visualization, with full web application integration.\n\n"
        "**Strict Clinical Safety Note**: Outputs raw model scores only. No arbitrary disease thresholds, "
        "positive/negative labels, or autonomous diagnostic decisions are provided. All outputs require "
        "interpretation by qualified medical professionals."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for cross-origin integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount statics
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

assets_dir = os.path.join(FRONTEND_DIST_DIR, "assets")
os.makedirs(assets_dir, exist_ok=True)
app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

# Mount modular API endpoints
app.include_router(api_router)


# Exception Handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc: ValueError):
    """Map ValueErrors to HTTP 400 Bad Request."""
    logger.warning(f"Bad Request (400): {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    """Catch-all exception handler to prevent leaking internal Python stack traces."""
    logger.error(f"Unhandled internal server error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred during processing."}
    )


@app.get("/")
async def get_index():
    dist_index = os.path.join(FRONTEND_DIST_DIR, "index.html")
    if os.path.exists(dist_index):
        return FileResponse(dist_index)
    return HTMLResponse("<h1>Chest X-ray AI Backend Server is Running</h1><p>Visit <a href='/docs'>/docs</a> for API documentation.</p>")


@app.get("/{file_path:path}")
async def serve_static_or_spa(file_path: str):
    """
    Serve static assets from frontend/dist (e.g., logo-icon.png, favicon.svg)
    and support Single Page Application (SPA) client-side routing fallback.
    """
    # Prevent intercepting API endpoints or documentation
    if file_path.startswith(("api/", "docs", "redoc", "openapi.json", "health", "predict", "gradcam", "analyze", "uploads", "static", "assets")):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")

    target_file = os.path.join(FRONTEND_DIST_DIR, file_path)
    if os.path.isfile(target_file):
        return FileResponse(target_file)

    dist_index = os.path.join(FRONTEND_DIST_DIR, "index.html")
    if os.path.exists(dist_index):
        return FileResponse(dist_index)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
