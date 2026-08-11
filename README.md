# Chest X-ray AI Inference Backend

A backend-only Chest X-ray analysis service built with **Python**, **PyTorch**, **TorchXRayVision**, **FastAPI**, and **Grad-CAM**.

The service accepts chest X-ray images, applies standardized TorchXRayVision image preprocessing, executes inference using the pretrained **DenseNet-121 (`res224-all`)** model, returns all raw pathology scores without artificial decision thresholds, and generates Grad-CAM heatmap overlays for consumer-selected pathologies.

---

## 1. Architecture

```text
                  Chest X-ray Image (JPG, JPEG, PNG)
                                 ↓
                            FastAPI API
                                 ↓
                     TorchXRayVision Preprocessing
                                 ↓
             TorchXRayVision DenseNet-121 (res224-all)
                                 ↓
                       Raw Pathology Scores
                                 │
                 ┌───────────────┴───────────────┐
                 ↓                               ↓
             /predict                        /gradcam
             /analyze                            ↓
                                         Selected Pathology
                                                 ↓
                                              Grad-CAM
                                                 ↓
                                         PNG Image Overlay
```

---

## 2. Key Technical Specifications

* **Pretrained Model**: TorchXRayVision DenseNet-121 (`weights="densenet121-res224-all"`). Loaded once at startup into memory.
* **Device Handling**: Automatically utilizes CUDA GPU if available, with seamless CPU fallback.
* **No Diagnostic Thresholds**: Strict adherence to returning raw model scores only. No artificial `positive`/`negative` thresholds are imposed.
* **Target Convolutional Layer**: Uses `model.features` (the final convolutional feature block of DenseNet-121 before spatial average pooling).
* **Hook Lifecycle**: Hooks are dynamically registered per Grad-CAM request and stripped in `finally` blocks to prevent memory leaks and hook accumulation.

---

## 3. Installation & Local Setup

### Step 1: Clone & Navigate

```bash
git clone <repository_url>
cd chest-xray-backend
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Run Service Options

**Option A: Integrated AvicennaX Medical Web UI & AI Server (Full-Stack)**

Run the integrated server with the React frontend and PyTorch DenseNet-121 backend:

```bash
python -m uvicorn avicennaX.app.main:app --reload
```

Access the AvicennaX web dashboard at `http://localhost:8000`.

**Option B: Standalone API Server Only**

Run the backend API server standalone:

```bash
uvicorn backend.main:app --reload
```

---

## 4. AvicennaX Frontend Integration

The backend is fully integrated into the **AvicennaX** clinical web application (`avicennaX/`):
* **Real AI Inference**: Uploading a Chest X-ray in the AvicennaX UI executes real TorchXRayVision DenseNet-121 inference across all 18 pathologies.
* **18 Pathology Score Grid**: Displays raw model scores for all 18 pathologies in an interactive selector (`ResultView.jsx`).
* **Dynamic Grad-CAM Visualizer**: Clicking any pathology dynamically re-generates and renders the real Grad-CAM visual heatmap overlay for that specific disease in real time.


---

## 4. API Endpoints Overview

FastAPI automatically generates interactive OpenAPI documentation:

* **Swagger UI**: `http://localhost:8000/docs`
* **ReDoc**: `http://localhost:8000/redoc`

| Method | Endpoint | Description | Content-Type |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Service status, model identifier, and device | `application/json` |
| `POST` | `/predict` | Accept X-ray image, return raw pathology scores | `multipart/form-data` |
| `POST` | `/analyze` | Accept X-ray image, return complete analysis | `multipart/form-data` |
| `POST` | `/gradcam` | Accept X-ray image & disease, return Grad-CAM PNG | `image/png` |

---

## 5. Integration & Usage Examples

### 5.1 Health Check (`curl`)

```bash
curl http://localhost:8000/health
```

**Example Response:**
```json
{
  "status": "ok",
  "model": "densenet121-res224-all",
  "device": "cpu"
}
```

### 5.2 Predict Endpoint (`curl`)

```bash
curl -X POST \
  http://localhost:8000/predict \
  -F "file=@chest_xray.jpg"
```

**Example Response:**
```json
{
  "model": "densenet121-res224-all",
  "predictions": [
    {
      "disease": "Atelectasis",
      "score": 0.213
    },
    {
      "disease": "Consolidation",
      "score": 0.071
    },
    {
      "disease": "Pneumonia",
      "score": 0.731
    }
  ]
}
```

### 5.3 Grad-CAM Endpoint (`curl`)

You can specify a target pathology, or omit the `disease` parameter to let the backend **automatically select the highest-scoring pathology**:

**Option A: Auto-select highest-scoring pathology**
```bash
curl -X POST \
  http://localhost:8000/gradcam \
  -F "file=@chest_xray.jpg" \
  --output gradcam_overlay.png
```

**Option B: Specific target pathology**
```bash
curl -X POST \
  http://localhost:8000/gradcam \
  -F "file=@chest_xray.jpg" \
  -F "disease=Pneumonia" \
  --output gradcam_overlay.png
```

*Note: The response includes an `X-Selected-Pathology` HTTP header indicating which pathology was used.*


---

### 5.4 Python Integration (`requests`)

```python
import requests

url = "http://localhost:8000"

# 1. Run raw pathology prediction
with open("chest_xray.jpg", "rb") as img_file:
    response = requests.post(f"{url}/predict", files={"file": img_file})
    print("Predictions:", response.json())

# 2. Request Grad-CAM visualization for a selected pathology
with open("chest_xray.jpg", "rb") as img_file:
    response = requests.post(
        f"{url}/gradcam",
        files={"file": img_file},
        data={"disease": "Pneumonia"}
    )
    if response.status_code == 200:
        with open("pneumonia_gradcam.png", "wb") as f:
            f.write(response.content)
        print("Grad-CAM overlay saved to pneumonia_gradcam.png")
    else:
        print("Error:", response.json())
```

---

## 6. Testing

Run the automated test suite with pytest:

```bash
pytest tests/ -v
```

---

## 7. Medical Safety & Clinical Disclaimer

> [!IMPORTANT]
> **This software is an AI-assisted research and decision-support tool, not an autonomous diagnostic system.**
>
> 1. Outputs are raw model prediction scores only and must **not** be interpreted as definitive clinical probabilities.
> 2. The system does **not** diagnose, declare disease presence/absence, or replace expert clinical judgement.
> 3. Grad-CAM visual heatmaps highlight features influencing model predictions; they do **not** serve as clinical proof of disease localization.
> 4. All outputs require interpretation and evaluation by qualified medical professionals. Independent clinical validation is required prior to deployment in clinical environments.
