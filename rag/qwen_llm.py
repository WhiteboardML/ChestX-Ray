"""
Qwen LLM Integration Module for AvicennaX RAG.
Supports Qwen2.5, Qwen2, Qwen-Coder via Ollama, vLLM, DashScope API, or local OpenAI-compatible endpoints.
"""
import os
import json
import logging
import requests
from typing import Dict, Any, List, Optional

logger = logging.getLogger("qwen_llm")

# Configuration via Environment Variables
QWEN_SERVER_URL = os.getenv("QWEN_SERVER_URL", "http://localhost:11434")
QWEN_MODEL_NAME = os.getenv("QWEN_MODEL_NAME", "qwen2.5")
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
QWEN_TIMEOUT = int(os.getenv("QWEN_TIMEOUT", "10"))


def generate_qwen_response(
    user_query: str,
    context_chunks: List[str],
    diagnosis: str = "Norma",
    lang: str = "uz"
) -> Dict[str, Any]:
    """
    Sends RAG retrieved context + query to Qwen LLM.
    If Qwen server is available, returns Qwen-generated medical response.
    Otherwise, gracefully falls back to structured RAG synthesis.
    """
    system_instructions = {
        "uz": (
            "Siz AvicennaX AI - tibbiy va pulmonologiya bo'yicha mutaxassis Qwen sun'iy intellekt modelisiz.\n\n"
            "JAVOB BERISH QOIDALARI VA STRUKTURASI:\n"
            "1. FAKTIK ISHONCHLILIK: Faqat taqdim etilgan klinik protokollar va kontekst asosida javob bering.\n"
            "2. TRIAGE VA SHOSHILINCHALIK HOLLATI: Har bir javobda shoshilinchlik darajasini (🚨 O'ta Shoshilinch, ⚠️ Yuqori, ⚡ O'rta, Normal) aniq ko'rsating.\n"
            "3. KLINIK HARAKATLAR: Protokol bo'yicha shifokor va bemor uchun tavsiyalarni bering.\n"
            "4. VRAC H KO'RIGI: Har doim yakuniy qaror va davolash kursi davolovchi vrach-pulmonolog tomonidan tasdiqlanishi shartligini eslatib o'ting."
        ),
        "ru": (
            "Вы — модель ИИ Qwen AvicennaX, специалист по медицинской пульмонологии.\n\n"
            "ПРАВИЛА И СТРУКТУРА ОТВЕТА:\n"
            "1. ФАКТИЧЕСКАЯ ОБОСНОВАННОСТЬ: Строго опирайтесь на предоставленные клинические протоколы и контекст.\n"
            "2. ТРИАЖ И УРОВЕНЬ СРОЧНОСТИ: Указывайте уровень срочности (🚨 Критический вызов, ⚠️ Высокая срочность, ⚡ Средняя срочность, Норма).\n"
            "3. КЛИНИЧЕСКИЕ ДЕЙСТВИЯ: Прописывайте рекомендации для врача по предоставленному протоколу.\n"
            "4. ВРАЧЕБНОЕ ПОДТВЕРЖДЕНИЕ: Обязательно напоминайте, что окончательное решение принимает лечащий врач-пульмонолог."
        ),
        "en": (
            "You are the Qwen AI medical model for AvicennaX Pulmonology.\n\n"
            "RESPONSE GUIDELINES & STRUCTURE:\n"
            "1. FACTUAL GROUNDING: Rely strictly on the provided clinical context and protocols.\n"
            "2. TRIAGE & URGENCY LEVEL: Clearly state urgency level (🚨 Critical Emergency, ⚠️ High Urgency, ⚡ Moderate Urgency, Normal).\n"
            "3. CLINICAL ACTIONS: Provide step-by-step clinical guidance based on the protocol.\n"
            "4. PHYSICIAN VERIFICATION: Always include a directive that final clinical management requires attending physician review."
        )
    }

    sys_prompt = system_instructions.get(lang, system_instructions["uz"])

    formatted_context = "\n\n".join(context_chunks) if context_chunks else "Klinik protokol konteksti topilmadi."

    user_prompt = (
        f"Klinik Tashxis: {diagnosis}\n"
        f"Topilgan Protokol Konteksti:\n{formatted_context}\n\n"
        f"Shifokor Savoli: {user_query}\n\n"
        f"Iltimos, taqdim etilgan protokollarga muvofiq professional javob shakllantiring."
    )

    # 1. Try Ollama Native API (http://localhost:11434/api/chat)
    ollama_url = f"{QWEN_SERVER_URL.rstrip('/')}/api/chat"
    payload = {
        "model": QWEN_MODEL_NAME,
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False
    }

    headers = {"Content-Type": "application/json"}
    if QWEN_API_KEY:
        headers["Authorization"] = f"Bearer {QWEN_API_KEY}"

    try:
        response = requests.post(ollama_url, json=payload, headers=headers, timeout=QWEN_TIMEOUT)
        if response.status_code == 200:
            res_json = response.json()
            reply_text = res_json.get("message", {}).get("content", "").strip()
            if reply_text:
                return {
                    "source": f"Qwen LLM ({QWEN_MODEL_NAME}) via Ollama",
                    "status": "success",
                    "text": reply_text
                }
    except Exception as e:
        logger.debug(f"Ollama Qwen endpoint not reachable at {ollama_url}: {e}")

    # 2. Try OpenAI-compatible endpoint (http://localhost:11434/v1/chat/completions)
    v1_url = f"{QWEN_SERVER_URL.rstrip('/')}/v1/chat/completions"
    payload_v1 = {
        "model": QWEN_MODEL_NAME,
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3
    }

    try:
        response_v1 = requests.post(v1_url, json=payload_v1, headers=headers, timeout=QWEN_TIMEOUT)
        if response_v1.status_code == 200:
            res_v1 = response_v1.json()
            reply_text = res_v1["choices"][0]["message"]["content"].strip()
            if reply_text:
                return {
                    "source": f"Qwen LLM ({QWEN_MODEL_NAME}) via v1/completions",
                    "status": "success",
                    "text": reply_text
                }
    except Exception as e:
        logger.debug(f"V1 Qwen endpoint not reachable at {v1_url}: {e}")

    # 3. Fallback when Qwen server is offline
    return {
        "source": "Local RAG Vector Engine (Qwen server offline)",
        "status": "fallback",
        "text": None
    }
