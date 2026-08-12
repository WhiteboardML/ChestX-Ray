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
            "Siz AvicennaX AI - O'zbekiston Respublikasi Sog'liqni saqlash vazirining 2025-yil 180-sonli buyrug'i bilan "
            "tasdiqlangan SOO'K / XOBL Milliy Klinik Standarti va Protokoli bo'yicha ishlovchi mutaxassis Qwen sun'iy intellekt modelisiz.\n\n"
            "JAVOB SHAKLLANTIRISHNING QAT'IY QOIDALARI:\n"
            "1. MATNNI QISQA VA LAKONIK TUTING: Uzun va ortiqcha gaplarsiz, faqat eng muhim klinik ma'lumotlarni bering.\n"
            "2. MANBA KO'RSATISH: Javobingizni har doim birinchi qatorda '📌 Manba: O'zbekiston SSV Milliy Klinik Standarti va Protokoli 2025 (180-sonli buyruq)' deb boshlang.\n"
            "3. DORI-DORILARNI NUQTA (BULLET POINT) BILAN RO'YXAT QILING: Barcha dori-darmonlar, dozalar va qabul qilish jadvallarini faqat nuqtalar ('•') bilan ro'yxat shaklida bering.\n"
            "4. VRAC H KO mezonlari: Oxirida shifokor ko'rigi zarurligini eslatib o'ting."
        ),
        "ru": (
            "Вы — модель ИИ Qwen AvicennaX, работающая по Национальному клиническому стандарту Узбекистана 2025 года "
            "(Приказ Минздрава РУз №180) по ХОБЛ и пульмонологии.\n\n"
            "СТРОГИЕ ПРАВИЛА ОФОРМЛЕНИЯ ОТВЕТА:\n"
            "1. КРАТКОСТЬ И ЛАКОНИЧНОСТЬ: Излагайте ответ максимально кратко, без лишних длинных текстов.\n"
            "2. УКАЗАНИЕ ИСТОЧНИКА: Всегда начинайте ответ с первой строки: '📌 Источник: Национальный клинический стандарт Минздрава РУз 2025 (Приказ №180)'.\n"
            "3. ЛЕКАРСТВА ТОЛЬКО ПО ПУНКТАМ (BULLET POINTS): Все лекарственные препараты, дозировки и курсы перечисляйте строго списком с точками ('•').\n"
            "4. ВРАЧЕБНЫЙ КОНТРОЛЬ: Напоминайте о необходимости подтверждения назначения врачом."
        ),
        "en": (
            "You are the Qwen AI medical model for AvicennaX, adhering to the Uzbekistan National Clinical Standard 2025 "
            "(MOH Order No. 180).\n\n"
            "STRICT RESPONSE FORMATTING RULES:\n"
            "1. BRIEF AND CONCISE: Keep the text short and directly to the point. Avoid long explanations.\n"
            "2. SOURCE CITATION: Always start the response on the very first line with: '📌 Source: Uzbekistan MOH National Clinical Standard 2025 (Order No. 180)'.\n"
            "3. MEDICATIONS IN BULLET POINTS: List all medications, exact dosages, daily frequencies, and treatment courses strictly as bullet points ('•').\n"
            "4. PHYSICIAN DIRECTIVE: Include brief reminder for attending physician confirmation."
        )
    }

    sys_prompt = system_instructions.get(lang, system_instructions["uz"])

    formatted_context = "\n\n".join(context_chunks) if context_chunks else "Klinik protokol va Milliy Standart konteksti topilmadi."

    user_prompt = (
        f"Klinik Tashxis: {diagnosis}\n"
        f"Topilgan SSV Milliy Klinik Standarti 2025 Konteksti:\n{formatted_context}\n\n"
        f"Shifokor Savoli: {user_query}\n\n"
        f"Iltimos, javobni QISQA qiling, birinchi qatorda MANBANI ko'rsating va barcha dori-darmonlarni NUQTALAR (•) bilan ro'yxat qiling."
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
