# LLM Integration Module (`llm/`)

This package provides LLM (Large Language Model) integration for **AvicennaX AI Chest X-ray Medical Diagnostics**.

It enables intelligent clinical report synthesis, patient-friendly Uzbek explanations, treatment precautions, and interactive medical Q&A chat for doctors.

---

## 1. Directory Structure

```text
llm/
├── __init__.py      # Package initialization & public API exports
├── client.py        # Gemini API client wrapper with fallback mechanism
├── prompts.py       # System instructions and medical prompt templates
├── service.py       # High-level report synthesis and chat assistant services
└── README.md        # Module documentation
```

---

## 2. Configuration & Setup

Set your Gemini API key in your environment:

```bash
export GEMINI_API_KEY="your_google_gemini_api_key_here"
```

On Windows PowerShell:

```powershell
$env:GEMINI_API_KEY="your_google_gemini_api_key_here"
```

*Note: If `GEMINI_API_KEY` is omitted, the module automatically operates in **rule-based fallback mode**, ensuring zero downtime or runtime errors.*

---

## 3. Usage Examples

### 3.1 Synthesize Medical Report

```python
from llm import synthesize_xray_report

report = synthesize_xray_report(
    diagnosis="Pnevmoniya (Pneumonia)",
    probability=89.0,
    urgency_title="🚨 O'TA SHOSHILINCH",
    raw_scores=[
        {"disease": "Pneumonia", "disease_uz": "Pnevmoniya", "score": 0.89},
        {"disease": "Atelectasis", "disease_uz": "Atelektaz", "score": 0.45}
    ]
)

print(report["llm_response"])
```

### 3.2 Medical Chat Assistant for Doctors

```python
from llm import chat_with_medical_llm

reply = chat_with_medical_llm(
    patient_id="MX-8924",
    diagnosis="Pnevmoniya",
    user_message="Ushbu bemor uchun tavsiya etiladigan birinchi bosqich antibiotik terapiyasi va doza ko'rsatmalari qanday?"
)

print(reply)
```
