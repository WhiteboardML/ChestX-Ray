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

## 📊 Project Presentation (PowerPoint)

The official presentation deck for the Navoi AI Hackathon is available in the repository:
- 📁 **[AvicennaX Presentation Deck (PPTX)](AvicennaX_Presentation.pptx)** (`AvicennaX_Presentation.pptx` — 11.08 MB)

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

### Step 4: Launch Application (Production Mode)
```bash
python main.py
```

### Step 5: Access in Browser
- **Clinical Web Application (Full-Stack UI)**: Open [http://localhost:8000](http://localhost:8000)
- **Log In**: Enter `admin@avicennaai.uz` / `AvicennaAI2026!`
- **Interactive API Documentation (Swagger)**: Open [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 💻 Running the Frontend (Development & Rebuild Options)

The repository includes pre-compiled frontend assets in `frontend/dist/`, so running `python main.py` serves the complete React Web UI out-of-the-box. 

If you wish to modify or develop the React frontend code, follow these options:

### Option A: Frontend Development Mode (Hot-Reloading)
For live frontend code modification with instant hot-reloading:

1. **Start Backend Server** (Terminal 1):
   ```bash
   python main.py
   ```

2. **Start React Vite Dev Server** (Terminal 2):
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

- **Live Hot-Reloading Web UI**: Open [http://localhost:5173](http://localhost:5173) (Proxies API requests automatically to `http://localhost:8000`).

### Option B: Rebuilding Frontend Assets for Production
If you make changes inside `frontend/src/` and want to compile new production assets:

```bash
cd frontend
npm install
npm run build
cd ..
python main.py
```

---

## 🏗️ Layered Architecture & Separation of Concerns (SoC)

The codebase has been refactored from a tightly coupled structure into distinct architectural layers to maximize testability, maintainability, and data security:

```text
       ┌────────────────────────────────────────────────────────┐
       │               ENTRYPOINTS & PRESENTATION               │
       │  - backend/main.py (App bootstrap & CORS config)        │
       │  - backend/api/v1/endpoints/ (FastAPI APIRouters)      │
       └───────────────────────────┬────────────────────────────┘
                                   │
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │                     SERVICE LAYER                      │
       │  - backend/services/inference_orchestrator.py          │
       │  - backend/services/report_generator.py (HTML reports) │
       └─────────────┬─────────────┬─────────────┬──────────────┘
                     │             │             │
                     ▼             ▼             ▼
       ┌────────────────────────┐ ┌───────────────┐ ┌───────────┐
       │   REPOSITORIES (DAL)   │ │ CORE ML & RAG │ │  CONFIG   │
       │  - patient_repository  │ │ - core/ml/    │ │ - config/ │
       │  - scan_repository     │ │ - core/rag/   │ │ - schemas/│
       │  - user_repository     │ │               │ │           │
       └────────────────────────┘ └───────────────┘ └───────────┘
```

1. **Presentation / API Routing Layer**: Handles purely HTTP concerns, CORS middlewares, static mounting, and request/response mapping via FastAPI routers ([`api/v1/endpoints/`](file:///Users/baxodir/Coding/ChestXray/ChestX-Ray/backend/api/v1/endpoints/)).
2. **Service Orchestration Layer**: Manages end-to-end transactional workflows (like parsing image uploads, running ML inference, computing urgency metrics, saving records, and compiling print reports) inside dedicated service classes ([`backend/services/`](file:///Users/baxodir/Coding/ChestXray/ChestX-Ray/backend/services/)).
3. **Core Engine Layer (PyTorch & Offline RAG)**: Isolated from web frameworks and databases. Handles pure machine learning predictions, Grad-CAM overlays ([`core/ml/`](file:///Users/baxodir/Coding/ChestXray/ChestX-Ray/backend/core/ml/)), and local vector search protocols ([`core/rag/`](file:///Users/baxodir/Coding/ChestXray/ChestX-Ray/backend/core/rag/)).
4. **Data Access Layer (Repository Pattern)**: Decoupled from serialization models. Coordinates database writes/reads via structured repositories ([`backend/repositories/`](file:///Users/baxodir/Coding/ChestXray/ChestX-Ray/backend/repositories/)) and data connection interfaces ([`backend/database/`](file:///Users/baxodir/Coding/ChestXray/ChestX-Ray/backend/database/)).
5. **Config & Schema Layer**: Organizes settings, bilingual translations ([`backend/config/`](file:///Users/baxodir/Coding/ChestXray/ChestX-Ray/backend/config/)), and modular Pydantic data schemas ([`backend/schemas/`](file:///Users/baxodir/Coding/ChestXray/ChestX-Ray/backend/schemas/)).

---

## 🛠️ Tech Stack & Key Components

* **AI Inference**: TorchXRayVision DenseNet-121 (`res224-all`) evaluating 18 chest pathologies + Normal baseline.
* **Explainability (XAI)**: Grad-CAM heatmap overlays calculated dynamically from `model.features` convolutional layers.
* **Clinical Protocol RAG**: Local TF-IDF & Cosine Similarity vector store over **Uzbekistan MOH Order No. 180 (2025)** COPD and Pneumonia clinical protocols.
* **Supported Image Formats**: `.png`, `.jpg`, `.jpeg`, `.dcm` (DICOM), `.pdf` (Radiological reports), `.webp`.
* **Database & Persistence**: SQLite via SQLAlchemy repositories.
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
