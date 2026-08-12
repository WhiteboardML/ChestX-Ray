"""
LLM Client implementation using Google Gemini API / GenAI SDK with fallback mechanisms.
"""
import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("llm_integration")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")


class LLMClient:
    """
    LLM Client for AvicennaX AI Chest X-ray Medical Assistant.
    Supports Google Gemini API with fallback to structured rule-based medical synthesis.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GEMINI_API_KEY
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """
        Enforces 100% Patient Data Privacy mode.
        External network API calls are disabled by default to prevent private medical data transmission.
        """
        logger.info("Patient Data Privacy Mode ENABLED. External cloud API calls are disabled. Running 100% offline local medical assistant.")
        self.client = None

    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
        Generate response from Gemini model or return smart fallback.
        """
        if self.client:
            try:
                config = {}
                if system_instruction:
                    config["system_instruction"] = system_instruction

                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=config if config else None
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                logger.error(f"Gemini API request failed: {e}. Falling back to default response.", exc_info=True)

        return self._fallback_generate(prompt)

    def _fallback_generate(self, prompt: str) -> str:
        """Smart fallback medical response when LLM API key is not configured."""
        if "Pnevmoniya" in prompt or "Pneumonia" in prompt:
            return (
                "Sun'iy intellekt rentgenogrammada pnevmoniya (o'pka yallig'lanishi) belgilarini aniqladi. "
                "Bemorga ko'p miqdorda iliq suyuqlik ichish, tana haroratini kuzatish va pulmonolog vrach ko'rigidan o'tish tavsiya etiladi."
            )
        elif "Atelektaz" in prompt or "Atelectasis" in prompt:
            return (
                "Rentgenogrammada o'pka segmentining gipoventilyatsiyasi (Atelektaz) alomatlari kuzatildi. "
                "Nafas mashqlari va vrach nazorati tavsiya etiladi."
            )
        elif "Norma" in prompt:
            return (
                "O'pka to'qimalari va a'zolari me'yorda. Hech qanday yaqqol patologik o'zgarishlar aniqlanmadi."
            )
        return (
            "Rentgenogramma tahlili yakunlandi. Shifokor-pulmonolog ko'rigiga murojaat qilish hamda "
            "qo'shimcha laboratoriya tahlillarini o'tkazish tavsiya etiladi."
        )


# Singleton LLM client instance
_llm_client_instance: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    global _llm_client_instance
    if _llm_client_instance is None:
        _llm_client_instance = LLMClient()
    return _llm_client_instance
