"""
LLM Integration Package for AvicennaX AI Chest X-ray Medical Diagnostics.
Provides Gemini AI integration for intelligent clinical report synthesis,
patient-friendly Uzbek explanations, treatment guidelines, and medical Q&A chat.
"""
from llm.service import synthesize_xray_report, chat_with_medical_llm

__all__ = ["synthesize_xray_report", "chat_with_medical_llm"]
