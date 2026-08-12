# AvicennaX AI — Chest X-Ray Clinical Diagnostics Platform

A full-stack, enterprise-grade Chest X-Ray AI Analysis & Clinical Decision Support System built with **FastAPI**, **PyTorch**, **TorchXRayVision**, **React (Vite)**, and **SQLite**.

---

## 🔑 Login Credentials (For Evaluators & Reviewers)

The system includes authentication. When the application starts up, the database automatically initializes the following default Admin/Doctor credentials:

| Field | Credential Value |
| :--- | :--- |
| **Email (Login)** | `admin@avicennaai.uz` |
| **Password (Parol)** | `AvicennaAI2026!` |
| **Role** | Bosh Shifokor (Admin) |
| **Subscription Plan** | SaaS Obunasi (Cheksiz / Unlimited) |

> 💡 **Note**: Simply enter these credentials on the login page when you launch `http://localhost:8000`.

---

## ⚡ Quick Start Guide (Clone & Run in 3 Minutes)

### Step 1: Clone Repository
```bash
git clone https://github.com/k-obloberdiyev/ChestX-Ray.git
cd ChestX-Ray
```

### Step 2: Create & Activate Virtual Environment (Isolated, non-global)

Do **not** install dependencies globally. Create a local, isolated Python virtual environment (`.venv`):

#### On Windows (PowerShell / CMD):
```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\Activate.ps1
```

#### On Linux / macOS:
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate
```

### Step 3: Install Dependencies inside Virtual Environment
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Launch Application
```bash
python main.py
```

### Step 5: Access in Browser
- **Clinical Web Application**: Open [http://localhost:8000](http://localhost:8000)
- **Log In**: Enter `admin@avicennaai.uz` / `AvicennaAI2026!`
- **Interactive API Documentation**: Open [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🏗️ System Architecture

```text
                  Chest X-Ray Image (PNG, JPG, DICOM .dcm, PDF)
                                       ↓
                           FastAPI Web Application
                                       ↓
                     TorchXRayVision Image Preprocessing
                                       ↓
                 TorchXRayVision DenseNet-121 (res224-all)
                                       ↓
                   Raw Pathology Scores & Grad-CAM Engine
                                       ↓
                      RAG Vector Engine & MOH Protocols
                                       ↓
                 React Web Interface (Bilingual UZ/RU/EN)
```

---

## 🛠️ Tech Stack & Key Components

* **AI Inference**: TorchXRayVision DenseNet-121 (`res224-all`) evaluating 18 chest pathologies + Normal baseline.
* **Explainability (XAI)**: Grad-CAM heatmap overlays calculated dynamically from `model.features` convolutional layers.
* **Clinical Protocol RAG**: Local TF-IDF & Cosine Similarity vector store over **Uzbekistan MOH Order No. 180 (2025)** COPD and Pneumonia clinical protocols.
* **Supported Image Formats**: `.png`, `.jpg`, `.jpeg`, `.dcm` (DICOM), `.pdf` (Radiological reports), `.webp`.
* **Database & Persistence**: SQLite via SQLAlchemy with automated migrations and seed profiles.
* **Frontend**: React 18, Vite, GFM Markdown renderer, Material Symbols, and TailwindCSS design system.

---

## 🧪 Automated Testing

Run the automated test suite covering API endpoints, database seeding, Grad-CAM generation, and RAG retrieval:

```bash
pytest -v
```

---

## 📜 Medical Safety & Clinical Disclaimer

> [!IMPORTANT]
> **This software is an AI-assisted research and decision-support tool, not an autonomous diagnostic system.**
>
> 1. Outputs are raw model prediction scores only and must **not** be interpreted as definitive clinical diagnoses.
> 2. The system does **not** replace expert clinical judgement by a licensed physician or radiologist.
> 3. Grad-CAM visual heatmaps highlight features influencing model predictions; they do **not** serve as sole clinical proof of disease localization.
