"""
High-level LLM Services for Medical Report Synthesis and Interactive Chat.
"""
from typing import Dict, Any, List
from llm.client import get_llm_client
from llm.prompts import (
    CLINICAL_SYSTEM_INSTRUCTION,
    REPORT_SYNTHESIS_PROMPT,
    CHAT_ASSISTANT_PROMPT
)


def synthesize_xray_report(
    diagnosis: str,
    probability: float,
    urgency_title: str,
    raw_scores: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Synthesize LLM medical report based on TorchXRayVision predictions and urgency.
    """
    client = get_llm_client()

    top_scores = sorted(raw_scores, key=lambda s: s.get("score", 0), reverse=True)[:5]
    raw_scores_formatted = "\n".join([
        f"- {p.get('disease_uz', p.get('disease'))}: {p.get('score', 0):.3f}"
        for p in top_scores
    ])

    prompt = REPORT_SYNTHESIS_PROMPT.format(
        diagnosis=diagnosis,
        probability=probability,
        urgency_title=urgency_title,
        raw_scores_formatted=raw_scores_formatted
    )

    response_text = client.generate_text(
        prompt=prompt,
        system_instruction=CLINICAL_SYSTEM_INSTRUCTION
    )

    return {
        "llm_response": response_text,
        "diagnosis": diagnosis,
        "probability": probability,
        "urgency_title": urgency_title,
        "is_llm_powered": client.client is not None
    }


def chat_with_medical_llm(patient_id: str, diagnosis: str, user_message: str) -> str:
    """
    Interactive Q&A assistant for doctors answering questions about diagnoses and treatment protocols.
    """
    client = get_llm_client()

    prompt = CHAT_ASSISTANT_PROMPT.format(
        patient_id=patient_id,
        diagnosis=diagnosis,
        message=user_message
    )

    return client.generate_text(
        prompt=prompt,
        system_instruction=CLINICAL_SYSTEM_INSTRUCTION
    )
