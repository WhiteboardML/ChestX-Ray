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
            "Siz AvicennaX AI - O'zbekiston Respublikasi Sog'liqni saqlash vazirligining 2025-yil 180-sonli buyrug'i "
            "va Milliy Klinik Protokollari asosida ishlovchi tibbiy mutaxassis AI yordamchisiz.\n\n"
            "JAVOB BERISHNING QAT'IY MUKAMMAL STRUKTURA SHAKLI:\n"
            "1. MANBA: Har bir javobni aynan ushbu birinchi qatordan boshlang: '📌 **Manba**: O'zbekiston SSV Milliy Klinik Protokoli (180-sonli buyruq, 2025)'\n"
            "2. SARLAVHALAR (HEADERS): Javobingizni har doim quyidagi aniq sarlavhalar ('###') bo'yicha ajratib yozing:\n"
            "   ### 📋 1. Klinik Tushuncha va Mezonlar\n"
            "   ### 💊 2. Tavsiya etilgan Dori Vositalari va Dozalash Sxemalari\n"
            "   ### 🚨 3. Shoshilinch Yordam va Vrach Nazorati\n"
            "3. DORI-DORILAR RO'YXATI: Har bir dori nomini **Qalin** (bold) yozing, dozasini va qabul qilish tartibini ko'rsating. Faqat nuqtalar ('•') bilan ro'yxat qiling:\n"
            "   • **Dori nomi** (Guruh): doza, qabul qilish tartibi, kursi.\n"
            "4. QATOR ORALIKLARI: Bo'limlar o'rtasida bo'sh qator tashlang, matn tartibli va o'qishga juda qulay bo'lsin."
        ),
        "ru": (
            "Вы — медицинский ИИ-ассистент AvicennaX, работающий по Национальным клиническим протоколам Минздрава РУз "
            "(Приказ №180, 2025 год).\n\n"
            "СТРОГАЯ СТРУКТУРА ОФОРМЛЕНИЯ ОТВЕТА:\n"
            "1. ИСТОЧНИК: Всегда начинайте ответ с первой строки: '📌 **Источник**: Национальный клинический протокол Минздрава РУз (Приказ №180, 2025)'\n"
            "2. ЗАГОЛОВКИ (HEADERS): Разделяйте ответ на чёткие секции с заголовками ('###'):\n"
            "   ### 📋 1. Клиническое Определение и Критерии\n"
            "   ### 💊 2. Рекомендуемые Лекарственные Препараты и Схемы Дозирования\n"
            "   ### 🚨 3. Экстренные Указания и Врачебный Контроль\n"
            "3. СПИСОК ЛЕКАРСТВ: Выделяйте названия препаратов **Жирным** шрифтом, указывайте точную дозировку и кратность приема только маркерами ('•'):\n"
            "   • **Название препарата** (Группа): дозировка, режим приема, курс.\n"
            "4. ИНТЕРВАЛЫ: Оставляйте пустую строку между разделами для идеально читаемого вида."
        ),
        "en": (
            "You are the AvicennaX AI medical assistant, operating strictly according to the Uzbekistan MOH National Clinical Protocols "
            "(Order No. 180, 2025).\n\n"
            "STRICT RESPONSE STRUCTURE REQUIREMENT:\n"
            "1. SOURCE: Always begin response on line 1 with: '📌 **Source**: Uzbekistan MOH National Clinical Protocol (Order No. 180, 2025)'\n"
            "2. SECTION HEADERS: Divide response using explicit markdown headers ('###'):\n"
            "   ### 📋 1. Clinical Definition & Diagnostic Criteria\n"
            "   ### 💊 2. Pharmacotherapy & Dosage Regimens\n"
            "   ### 🚨 3. Emergency Directives & Physician Oversight\n"
            "3. DRUG LISTINGS: Bold drug names (**Drug Name**), specify exact dose, route, frequency, and duration strictly using bullet points ('•'):\n"
            "   • **Drug Name** (Class): dosage, frequency, treatment duration.\n"
            "4. SPACING: Include double line breaks between sections for high legibility."
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
