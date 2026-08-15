from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel

from backend.core.rag.rag_engine import query_rag_assistant

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    diagnosis: Optional[str] = "Norma"
    patient_id: Optional[str] = None
    lang: Optional[str] = "uz"


@router.post("/api/chat")
async def chat_assistant(req: ChatRequest):
    """
    Local Offline RAG Medical Q&A Assistant.
    Retrieves official SSV medical protocols & grounds advice locally for 100% data privacy.
    """
    pid = req.patient_id or "UNKNOWN"
    diag = req.diagnosis or "Norma"
    msg = req.message or ""
    language = req.lang or "uz"

    rag_result = query_rag_assistant(
        patient_id=pid,
        diagnosis=diag,
        user_message=msg,
        lang=language
    )

    return {
        "message": rag_result["message"],
        "is_rag_grounded": rag_result["is_rag_grounded"],
        "citations": rag_result["citations"]
    }
