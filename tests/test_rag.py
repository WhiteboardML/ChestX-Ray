"""
Unit Tests for Local RAG Engine & Vector Store.
"""
from rag.vector_store import LocalVectorStore, get_vector_store
from rag.rag_engine import query_rag_assistant, build_rag_report


def test_vector_store_indexing_and_search():
    store = get_vector_store()
    results = store.search("Pnevmoniya", top_k=1, lang="uz")
    assert len(results) > 0
    doc, score = results[0]
    assert doc["disease"] == "Pneumonia"
    assert score > 0.0


def test_rag_query_assistant_grounding():
    result = query_rag_assistant(
        patient_id="PAT-TEST",
        diagnosis="Pneumonia",
        user_message="pnevmoniya dori va isitma",
        lang="uz"
    )
    assert result["is_rag_grounded"] is True
    assert len(result["citations"]) > 0
    assert "Pneumonia" in result["citations"][0]["disease"]


def test_rag_multilingual_support():
    result_ru = query_rag_assistant(
        patient_id="PAT-TEST",
        diagnosis="Pneumothorax",
        user_message="пневмоторакс экстренный",
        lang="ru"
    )
    assert result_ru["is_rag_grounded"] is True
    assert "Пневмоторакс" in result_ru["message"] or "Клинический" in result_ru["message"]


def test_qwen_integration_fallback():
    from rag.qwen_llm import generate_qwen_response
    res = generate_qwen_response(
        user_query="Pnevmoniya bo'yicha yo'riqnoma",
        context_chunks=["Pnevmoniya klinik davolash protokoli"],
        diagnosis="Pneumonia",
        lang="uz"
    )
    assert "status" in res
    assert "source" in res

