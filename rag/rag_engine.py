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
            reply = (
                f"📌 **Источник**: Национальный клинический протокол Минздрава РУз (Приказ №180, 2025)\n\n"
                f"### 📋 Клинические Рекомендации по Диагнозу [{diagnosis}]:\n\n"
                f"{context_str}\n\n"
                f"### 🚨 Важное Замечание:\n"
                f"• Назначение и коррекция лекарственных средств подлежат обязательной верификации врачом-пульмонологом."
            )
        elif lang == "en":
            reply = (
                f"📌 **Source**: Uzbekistan MOH National Clinical Protocol (Order No. 180, 2025)\n\n"
                f"### 📋 Clinical Guideline for [{diagnosis}]:\n\n"
                f"{context_str}\n\n"
                f"### 🚨 Important Notice:\n"
                f"• All medication regimens and dosage adjustments require attending physician confirmation."
            )
        else:
            reply = (
                f"📌 **Manba**: O'zbekiston SSV Milliy Klinik Protokoli (180-sonli buyruq, 2025)\n\n"
                f"### 📋 [{diagnosis}] Bo'yicha Milliy Klinik Tavsiyalar:\n\n"
                f"{context_str}\n\n"
                f"### 🚨 Muhim Eslatma:\n"
                f"• Barcha dori-darmon tayinlovlari va dozalash sxemalari vrach-pulmonolog ko'rigi orqali tasdiqlanishi shart."
            )
    else:
        model_source = "Local Vector RAG Engine"
        if lang == "ru":
            reply = (
                f"📌 **Источник**: Минздрав РУз (Приказ №180)\n\n"
                f"### 📋 Рекомендация при [{diagnosis}]:\n\n"
                f"• Проведение консультации пульмонолога и повторная рентгенография ОГК через 7-10 дней.\n"
                f"• Оценка клиники и лаборатории (СРБ, ОАК)."
            )
        elif lang == "en":
            reply = (
                f"📌 **Source**: Uzbekistan MOH Guidelines (Order No. 180)\n\n"
                f"### 📋 Directive for [{diagnosis}]:\n\n"
                f"• Specialist pulmonologist consultation and follow-up chest X-ray in 7-10 days.\n"
                f"• Complete blood count and CRP inflammatory markers evaluation."
            )
        else:
            reply = (
                f"📌 **Manba**: O'zbekiston SSV Standarti (180-sonli buyruq)\n\n"
                f"### 📋 [{diagnosis}] Bo'yicha Tavsiya:\n\n"
                f"• Vrach-pulmonolog ko'rigi va 7-10 kundan so'ng qayta rentgen tahlili o'tkazish.\n"
                f"• Umumiy qon va SRO (C-reaktiv oqsil) laborator tahlillarini nazorat qilish."
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
