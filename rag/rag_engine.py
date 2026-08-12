"""
Local RAG Engine: Retrieves protocol knowledge & generates fact-grounded clinical responses.
"""
from typing import Dict, Any, List, Optional
from rag.vector_store import get_vector_store
from rag.qwen_llm import generate_qwen_response


def query_rag_assistant(
    patient_id: str,
    diagnosis: str,
    user_message: str,
    lang: str = "uz"
) -> Dict[str, Any]:
    """
    RAG Query Assistant for Doctors & Clinicians using Qwen LLM + SSV protocols.
    Retrieves matching SSV protocols from local vector store and synthesizes grounded answer via Qwen.
    """
    vector_store = get_vector_store()
    search_query = f"{diagnosis} {user_message}"
    matched_results = vector_store.search(search_query, top_k=2, lang=lang)

    context_chunks = []
    protocol_citations = []

    for doc, score in matched_results:
        protocol_citations.append({
            "protocol_id": doc.get("id"),
            "disease": doc.get("disease"),
            "similarity_score": round(score, 3)
        })

        if lang == "ru":
            context_chunks.append(f"📌 {doc.get('title_ru')}:\n{doc.get('content_ru')}")
        elif lang == "en":
            context_chunks.append(f"📌 {doc.get('title_en')}:\n{doc.get('content_en')}")
        else:
            context_chunks.append(f"📌 {doc.get('title_uz')}:\n{doc.get('content_uz')}")

    # Pass context + prompt to Qwen LLM
    qwen_res = generate_qwen_response(
        user_query=user_message,
        context_chunks=context_chunks,
        diagnosis=diagnosis,
        lang=lang
    )

    if qwen_res["status"] == "success" and qwen_res.get("text"):
        reply = qwen_res["text"]
        model_source = qwen_res["source"]
    elif context_chunks:
        model_source = "Local Vector RAG Engine"
        context_str = "\n\n".join(context_chunks)
        if lang == "ru":
            reply = f"На основе клинических протоколов Минздрава по диагнозу [{diagnosis}]:\n\n{context_str}\n\n⚠️ Обратите внимание: Все назначения делаются врачом-пульмонологом на личном приеме."
        elif lang == "en":
            reply = f"Based on MOH clinical protocols for [{diagnosis}]:\n\n{context_str}\n\n⚠️ Note: All treatments must be confirmed by a consulting physician."
        else:
            reply = f"SSV ning [{diagnosis}] bo'yicha tasdiqlangan klinik protokoli va yo'riqnomasi asosida:\n\n{context_str}\n\n⚠️ Eslatma: Barcha dori vositalari vrach-pulmonolog tomonidan shaxsiy ko'rikda tayinlanadi."
    else:
        model_source = "Local Vector RAG Engine"
        if lang == "ru":
            reply = f"По диагнозу [{diagnosis}] рекомендуется стационарный или амбулаторный контроль пульмонолога, проведение лабораторных анализов крови и повторная рентгенография через 7-10 дней."
        elif lang == "en":
            reply = f"For diagnosis [{diagnosis}], pulmonologist outpatient review, blood laboratory tests, and follow-up X-ray imaging in 7-10 days are recommended."
        else:
            reply = f"Ushbu [{diagnosis}] tahlili bo'yicha SSV yo'riqnomasi asosida: Vrach-pulmonolog ko'rigi, qon va balg'am tahlillari hamda 7-10 kundan so'ng takroriy rentgenografiya tavsiya etiladi."

    return {
        "message": reply,
        "is_rag_grounded": len(context_chunks) > 0,
        "citations": protocol_citations,
        "source": model_source
    }


def build_rag_report(
    diagnosis: str,
    probability: float,
    raw_scores: List[Dict[str, Any]],
    lang: str = "uz"
) -> Dict[str, Any]:
    """
    RAG-driven diagnostic report builder grounding findings in SSV guidelines.
    """
    vector_store = get_vector_store()
    results = vector_store.search(diagnosis, top_k=1, lang=lang)

    protocol_info = results[0][0] if results else None

    if protocol_info:
        if lang == "ru":
            guideline = protocol_info.get("content_ru")
        elif lang == "en":
            guideline = protocol_info.get("content_en")
        else:
            guideline = protocol_info.get("content_uz")
    else:
        guideline = "Ambulator kuzatuv va shifokor ko'rigi tavsiya etiladi."

    return {
        "diagnosis": diagnosis,
        "probability": probability,
        "clinical_guideline": guideline,
        "protocol_id": protocol_info.get("id") if protocol_info else None
    }
