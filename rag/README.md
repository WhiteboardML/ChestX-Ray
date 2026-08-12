# Local RAG (Retrieval-Augmented Generation) Architecture (`rag/`)

This package provides a **100% Local, Offline, Privacy-Compliant RAG Engine** for **AvicennaX AI Chest X-ray Diagnostics**.

It grounds diagnostic answers, clinical recommendations, and doctor Q&A assistant responses in official Ministry of Health (SSV) pulmonology treatment protocols and clinical guidelines without sending any patient data over external networks.

---

## 1. Directory Structure

```text
rag/
├── __init__.py               # Public RAG exports (query_rag_assistant, build_rag_report)
├── knowledge/
│   └── ssv_protocols.json    # Clinical treatment protocols & guidelines DB
├── vector_store.py           # Inverted TF-IDF index & Cosine Similarity search engine
├── rag_engine.py             # Context retrieval & medical response generator
└── README.md                 # Package documentation
```

---

## 2. RAG Pipeline Architecture

```text
Doctor Query / Scan Findings
         │
         ▼
[Local Tokenizer & TF-IDF Vectorizer]
         │
         ▼
[Cosine Similarity Vector Search]
         │
         ▼
[Matched Top-K SSV Clinical Protocols]
         │
         ▼
[Local RAG Synthesizer (UZ / RU / EN)]
         │
         ▼
Grounded Medical Answer + Protocol Citations
```

---

## 3. Usage Examples

### 3.1 Doctor Q&A Assistant Query

```python
from rag import query_rag_assistant

result = query_rag_assistant(
    patient_id="MX-8924",
    diagnosis="Pnevmoniya",
    user_message="Isitma va nafas qisishi kuzatilganda dori dozasini ko'rsating",
    lang="uz"
)

print(result["message"])
print("RAG Grounded:", result["is_rag_grounded"])
print("Citations:", result["citations"])
```

### 3.2 Medical Protocol Grounded Synthesis

```python
from rag import build_rag_report

report = build_rag_report(
    diagnosis="Pneumothorax",
    probability=89.5,
    raw_scores=[],
    lang="ru"
)

print(report["clinical_guideline"])
```
