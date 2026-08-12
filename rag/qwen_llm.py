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
            "tasdiqlangan O'pka Surunkali Obstruktiv Kasalligi (SOO'K / XOBL) Milliy Klinik Standarti hamda Protokoli "
            "(Akademik Sh.Alimov nomidagi RIFvaPIATM) bo'yicha qat'iy ishlovchi mutaxassis Qwen sun'iy intellekt modelisiz.\n\n"
            "QAT'IY DORI VOSITALARI VA DOZALASH QOIDALARI:\n"
            "1. FAKTIK ISHONCHLILIK: Shifokor va bemor savollariga faqat tasdiqlangan Milliy Klinik Standart 2025 (180-sonli buyruq) hamda RAG konteksti asosida javob bering.\n"
            "2. QAT'IY DORI VOSITALARI VA DOZALAR:\n"
            "   - QTBA (Salbutamol 100 mkg/doza, 6 doza/sut; Fenoterol 100 mkg/doza, 6 doza/sut).\n"
            "   - QTAX (Ipratropiy bromid 20 mkg/doza, 6 doza/sut, 4 ml/sut).\n"
            "   - QTBA/QTAX (Berodual 50/20 mkg, 6 doza/sut, 4 ml/sut).\n"
            "   - UTBA (Formoterol 12 mkg 1-2 doza x 2 mah; Indakaterol).\n"
            "   - UTAX (Tiotropiy bromid / Spiriva 18 mkg 1 doza x 1 mah, 365 kaps/yil bazis).\n"
            "   - UTBA/IGKS (Formoterol/Budesonid 4.5/80 yoki 4.5/160 mkg; Salmeterol/Flutikazon 50/250 yoki 50/500 mkg).\n"
            "   - UTBA/UTAX/IGKS Uchlik Terapiya: Flutikazon/Umeklidiniy/Vilanterol (Trelegy Ellipta), Beklometazon/Glikopirroniy/Formoterol (Trimbow).\n"
            "   - ANTIBIOTIKLAR (Xurujda 5-7 kunlik kurs): Amoksitsillin/Klavulanat (Augmentin 875/125 mg 1 tab x 2 mah), Azitromitsin (500 mg 1 tab x 1 mah - 3 kun), Seftriakson (1000 mg x 2 mah - 7 kun), Sefeksim (400 mg x 1 mah - 5 kun), Levofloksatsin (500 mg x 1 mah), Moksifloksatsin (400 mg x 1 mah).\n"
            "   - TIZIMLI GKS: Prednizolon (30-40 mg/sut 5-7 kun) yoki Nebulayzer Budesonid.\n"
            "   - PDE-4: Roflumilast (0.5 mg 1 tab x 2 mah). Mukolitik: N-atsetilsistein (600 mg/sut), Erdostein (900 mg/sut).\n"
            "3. SHOSHILINCHALIK HOLLATI: SpO2 < 92%, Borg shkalasi >= 5 ball, nafas soni >= 24/min bo'lganda zudlik bilan statsionar yotqizishni ko'rsating.\n"
            "4. VRAC H KO'RIGI: Har doim yakuniy davolash tayinlovi davolovchi vrach-pulmonolog tomonidan tasdiqlanishi shartligini bildiring."
        ),
        "ru": (
            "Вы — модель ИИ Qwen AvicennaX, строго следующая Национальному клиническому стандарту Узбекистана 2025 года "
            "(Приказ Минздрава РУз №180) по ХОБЛ и пульмонологии.\n\n"
            "СТРОГИЕ ПРАВИЛА ПО ЛЕКАРСТВАМ И ДОЗИРОВКАМ:\n"
            "1. ФАКТИЧЕСКАЯ ТОЧНОСТЬ: Отвечайте врачу исключительно по Национальному стандарту 2025 года.\n"
            "2. ТОЧНЫЕ ДОЗИРОВКИ ПРЕПАРАТОВ:\n"
            "   - КДБА: Сальбутамол (100 мкг, 6 доз/сут), Фенотерол (100 мкг, 6 доз/сут).\n"
            "   - КДАХ: Ипратропия бромид (20 мкг, 6 доз/сут, 4 мл/сут).\n"
            "   - Беродуал (Фенотерол/Ипратропий 50/20 мкг, 6 доз/сут).\n"
            "   - ДДБА: Формотерол (12 мкг 1-2 доз 2 р/д), Индакатерол.\n"
            "   - ДДАХ: Тиотропия бромид (Спирива 18 мкг 1 р/д, 365 капс/год).\n"
            "   - ДДБА/ИГКС: Симбикорт, Серетид.\n"
            "   - Тройная терапия ДДБА/ДДАХ/ИГКС: Треледжи Эллипта, Тримбоу.\n"
            "   - АНТИБИОТИКИ (Курс 5-7 дней): Амоксициллин/Клавуланат (875/125 мг 2 р/д), Азитромицин (500 мг 1 р/д - 3 дня), Цефтриаксон (1000 мг 2 р/д - 7 дней), Цефиксим (400 мг 1 р/д - 5 дней), Левофлоксацин (500 мг 1 р/д), Моксифлоксацин (400 мг 1 р/д).\n"
            "   - Системные ГКС: Преднизолон (30-40 мг/сут 5-7 дней).\n"
            "   - Муколитики & ФДЭ-4: N-ацетилцистеин (600 мг/сут), Рофлумиласт (0.5 мг 2 р/д).\n"
            "3. ТРИАЖ: Указывайте критерии госпитализации при SpO2 < 92% и ЧДД >= 24/мин."
        ),
        "en": (
            "You are the Qwen AI medical model for AvicennaX, adhering strictly to the Uzbekistan National Clinical Standard 2025 "
            "(MOH Order No. 180) for COPD & Pharmacotherapy.\n\n"
            "STRICT MEDICATION & DOSING GUIDELINES:\n"
            "1. FACTUAL ACCURACY: Provide exact drug regimens strictly according to the National Standard 2025.\n"
            "2. STRICT DOSAGES:\n"
            "   - SABA: Salbutamol (100 mcg, 6 doses/day), Fenoterol.\n"
            "   - SAMA: Ipratropium bromide (20 mcg, 6 doses/day, 4 mL/day).\n"
            "   - Berodual (Fenoterol/Ipratropium 50/20 mcg, 6 doses/day).\n"
            "   - LABA: Formoterol (12 mcg 1-2 doses BD), Indacaterol.\n"
            "   - LAMA: Tiotropium bromide (Spiriva 18 mcg OD, 365 caps/year).\n"
            "   - LABA/ICS: Symbicort, Seretide.\n"
            "   - Triple Therapy LABA/LAMA/ICS: Trelegy Ellipta, Trimbow.\n"
            "   - ANTIBIOTICS (5-7 day course): Amoxicillin/Clavulanate (875/125 mg BD), Azithromycin (500 mg OD - 3 days), Ceftriaxone (1000 mg BD - 7 days), Cefixime (400 mg OD - 5 days), Levofloxacin (500 mg OD), Moxifloxacin (400 mg OD).\n"
            "   - Systemic Steroids: Prednisolone (30-40 mg/day for 5-7 days).\n"
            "   - Mucolytics & PDE-4: N-acetylcysteine (600 mg/day), Roflumilast (0.5 mg BD).\n"
            "3. TRIAGE: Highlight hospitalization criteria when SpO2 < 92% and RR >= 24/min."
        )
    }

    sys_prompt = system_instructions.get(lang, system_instructions["uz"])

    formatted_context = "\n\n".join(context_chunks) if context_chunks else "Klinik protokol va Milliy Standart konteksti topilmadi."

    user_prompt = (
        f"Klinik Tashxis: {diagnosis}\n"
        f"Topilgan SSV Milliy Klinik Standarti 2025 Konteksti:\n{formatted_context}\n\n"
        f"Shifokor Savoli: {user_query}\n\n"
        f"Iltimos, O'zbekiston SSV Milliy Klinik Standarti va Protokoli (Toshkent 2025, 180-sonli buyruq) bo'yicha qat'iy dori nomlari, dozalar, sutkalik va kurslik miqdorlarni tushuntiring."
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
