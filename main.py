"""
Main application entry point.
Exposes the FastAPI app from backend.main.

Run options:
  python main.py
  python backend/main.py
  uvicorn main:app --reload
  uvicorn backend.main:app --reload
"""
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.main import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)

