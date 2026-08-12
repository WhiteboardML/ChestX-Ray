"""
RAG (Retrieval-Augmented Generation) Package for AvicennaX AI.
Provides 100% local, offline, privacy-compliant vector retrieval and clinical protocol grounding.
"""
from rag.rag_engine import query_rag_assistant, build_rag_report

__all__ = ["query_rag_assistant", "build_rag_report"]
