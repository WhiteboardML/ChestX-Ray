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
        context_str = "\n".join(context_chunks)
        if lang == "ru":
            reply = (
                f"📌 Источник: Национальный клинический стандарт Минздрава РУз 2025 (Приказ №180)\n\n"
                f"💡 Краткая рекомендация по диагнозу [{diagnosis}]:\n"
                f"{context_str}\n\n"
                f"⚠️ Назначение лекарств подтверждается врачом-пульмонологом."
            )
        elif lang == "en":
            reply = (
                f"📌 Source: Uzbekistan MOH National Clinical Standard 2025 (Order No. 180)\n\n"
                f"💡 Summary Recommendation for [{diagnosis}]:\n"
                f"{context_str}\n\n"
                f"⚠️ Medication regimens require attending physician confirmation."
            )
        else:
            reply = (
                f"📌 Manba: O'zbekiston SSV Milliy Klinik Standarti va Protokoli 2025 (180-sonli buyruq)\n\n"
                f"💡 [{diagnosis}] bo'yicha qisqa klinik tavsiya:\n"
                f"{context_str}\n\n"
                f"⚠️ Eslatma: Dori vositalari tayinlovi vrach-pulmonolog tomonidan tasdiqlanishi shart."
            )
    else:
        model_source = "Local Vector RAG Engine"
        if lang == "ru":
            reply = (
                f"📌 Источник: Минздрав РУз (Приказ №180)\n\n"
                f"• По диагнозу [{diagnosis}] рекомендуется осмотр пульмонолога и повторная рентгенография через 7-10 дней."
            )
        elif lang == "en":
            reply = (
                f"📌 Source: Uzbekistan MOH (Order No. 180)\n\n"
                f"• For diagnosis [{diagnosis}], pulmonologist review and follow-up X-ray in 7-10 days are recommended."
            )
        else:
            reply = (
                f"📌 Manba: O'zbekiston SSV (180-sonli buyruq)\n\n"
                f"• Ushbu [{diagnosis}] bo'yicha vrach-pulmonolog ko'rigi hamda 7-10 kundan so'ng qayta rentgen tahlili tavsiya etiladi."
            )

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
