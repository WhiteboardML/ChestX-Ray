import os
import torch

MODEL_NAME = "densenet121-res224-all"
IMAGE_SIZE = 224
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

PATHOLOGY_TRANSLATIONS_UZ = {
    "Norma": "Norma (Me'yorda)",
    "Atelectasis": "Atelektaz",
    "Consolidation": "Konsolidatsiya",
    "Infiltration": "Infiltratsiya",
    "Pneumothorax": "Pnevmotoraks",
    "Edema": "O'pka shishi",
    "Emphysema": "Emfizema",
    "Fibrosis": "Fibroz",
    "Effusion": "Plevral efuziya",
    "Pneumonia": "Pnevmoniya",
    "Pleural_Thickening": "Plevra qalinlashishi",
    "Cardiomegaly": "Kardiomegaliya",
    "Nodule": "O'pka tuguni",
    "Mass": "Hajmli hosila",
    "Hernia": "Churra",
    "Lung Lesion": "O'pka zararlanishi",
    "Fracture": "Qovurg'a sinishi",
    "Lung Opacity": "O'pka xiralashishi",
    "Enlarged Cardiomediastinum": "Kengaygan kardiomediastinum"
}

# Reverse mapping for flexible lookup
UZ_TO_EN_PATHOLOGY = {v.lower(): k for k, v in PATHOLOGY_TRANSLATIONS_UZ.items()}
for k, v in PATHOLOGY_TRANSLATIONS_UZ.items():
    UZ_TO_EN_PATHOLOGY[k.lower()] = k


def get_pathology_uz(name: str) -> str:
    """Return Uzbek translation for a pathology name."""
    if not name:
        return ""
    return PATHOLOGY_TRANSLATIONS_UZ.get(name, UZ_TO_EN_PATHOLOGY.get(name.lower(), name))


def get_pathology_en(name: str) -> str:
    """Return English pathology identifier for a given English or Uzbek pathology name."""
    if not name:
        return ""
    return UZ_TO_EN_PATHOLOGY.get(name.lower(), name)


def get_default_device() -> torch.device:
    """Return CUDA device if available, otherwise CPU."""
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")

