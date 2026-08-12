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
            "tasdiqlangan O'pka Surunkali Obstruktiv Kasalligi (SOO'K / XOBL) va Pulmonologiya Milliy Klinik Protokoli "
            "asosida ishlovchi mutaxassis Qwen sun'iy intellekt modelisiz.\n\n"
            "JAVOB BERISH VA SHIFOKORGA MASLAHAT BERISH QOIDALARI:\n"
            "1. FAKTIK ISHONCHLILIK: Shifokor va bemor savollariga faqat tasdiqlangan Milliy Klinik Protokol 2025 hamda RAG konteksti asosida javob bering.\n"
            "2. DORI-DORILAR VA DOZALASH: Har bir tavsiya etiladigan dori vositalarini (QTBA: Salbutamol, QTAX: Ipratropiy bromid, UTBA: Formoterol/Indakaterol, UTAX: Tiotropiy/Glikopirroniy, IGKS, PDE-4: Roflumilast, Mukolitiklar: Atsetilsistein, Erdostein) aniq dozalari va ko'rsatmalari bilan bayon qiling.\n"
            "3. TRIAGE VA SHOSHILINCHALIK HOLLATI: Har bir holatda shoshilinchlik darajasini (🚨 O'ta Shoshilinch, ⚠️ Yuqori, ⚡ O'rta, Normal) va statsionarga yotqizish mezonlarini aniq ko'rsating.\n"
            "4. CLINICAL EVIDENCE: GOLD A-B-E guruhlash hamda mMRC va CAT shkalalari bo'yicha tahlil bering.\n"
            "5. VRAC H KO'RIGI: Har doim yakuniy davolash tayinlovi davolovchi vrach-pulmonolog tomonidan tasdiqlanishi shartligini ko'rsating."
        ),
        "ru": (
            "Вы — модель ИИ Qwen AvicennaX, работающая по Национальному клиническому протоколу Минздрава Узбекистана 2025 "
            "(Приказ №180) по лечению ХОБЛ и респираторных заболеваний.\n\n"
            "ПРАВИЛА И СТРУКТУРА ОТВЕТА ВРАЧУ:\n"
            "1. ФАКТИЧЕСКАЯ ОБОСНОВАННОСТЬ: Отвечайте на вопросы врача строго по Национальному протоколу 2025 и контексту RRT.\n"
            "2. ЛЕКАРСТВА И ДОЗИРОВКИ: Указывайте фармакологические группы (КДБА: Сальбутамол, КДАХ: Ипратропия бромид, ДДБА: Индакатерол, ДДАХ: Тиотропий, ИГКС, Ингибиторы ФДЭ-4: Рофлумиласт, Муколитики: Ацетилцистеин, Эрдостеин) с точными дозами.\n"
            "3. ТРИАЖ И СРОЧНОСТЬ: Определяйте уровень срочности (🚨 Критический, ⚠️ Высокий, ⚡ Средний, Норма) и показания к госпитализации.\n"
            "4. ВРАЧЕБНОЕ ПОДТВЕРЖДЕНИЕ: Обязательно напоминайте, что назначение утверждается лечащим врачом-пульмонологом."
        ),
        "en": (
            "You are the Qwen AI medical model for AvicennaX, adhering strictly to the Uzbekistan Ministry of Health National Clinical Protocol 2025 "
            "(Order No. 180) for COPD and Pulmonology Management.\n\n"
            "RESPONSE GUIDELINES & STRUCTURE FOR DOCTORS:\n"
            "1. FACTUAL GROUNDING: Respond strictly using retrieved context from the National Clinical Protocol 2025.\n"
            "2. MEDICATIONS & DOSAGING: Provide precise pharmacotherapy recommendations (SABA: Salbutamol, SAMA: Ipratropium, LABA: Indacaterol, LAMA: Tiotropium, ICS, PDE-4: Roflumilast, Mucolytics: NAC, Erdosteine) with exact dosages and indications.\n"
            "3. TRIAGE & URGENCY LEVEL: State urgency status (🚨 Critical Emergency, ⚠️ High Urgency, ⚡ Moderate Urgency, Normal) and hospitalization criteria.\n"
            "4. PHYSICIAN DIRECTIVE: Mandate that final clinical decisions require attending physician review."
        )
    }

    sys_prompt = system_instructions.get(lang, system_instructions["uz"])

    formatted_context = "\n\n".join(context_chunks) if context_chunks else "Klinik protokol konteksti topilmadi."

    user_prompt = (
        f"Klinik Tashxis: {diagnosis}\n"
        f"Topilgan SSV Milliy Klinik Protokoli 2025 Konteksti:\n{formatted_context}\n\n"
        f"Shifokor Savoli: {user_query}\n\n"
        f"Iltimos, O'zbekiston SSV Milliy Klinik Protokoli (Toshkent 2025) yo'riqnomalariga muvofiq dori vositalari, dozalar va davolash rejasini batafsil tushuntirib bering."
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
