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

PATHOLOGY_TRANSLATIONS_RU = {
    "Norma": "Норма",
    "Atelectasis": "Ателектаз",
    "Consolidation": "Консолидация",
    "Infiltration": "Инфильтрация",
    "Pneumothorax": "Пневмоторакс",
    "Edema": "Отек легких",
    "Emphysema": "Эмфизема",
    "Fibrosis": "Фиброз",
    "Effusion": "Плевральный выпот",
    "Pneumonia": "Пневмония",
    "Pleural_Thickening": "Утолщение плевры",
    "Cardiomegaly": "Кардиомегалия",
    "Nodule": "Узелок легкого",
    "Mass": "Объемное образование",
    "Hernia": "Грыжа",
    "Lung Lesion": "Поражение легких",
    "Fracture": "Перелом ребра",
    "Lung Opacity": "Затемнение легкого",
    "Enlarged Cardiomediastinum": "Расширение средостения"
}

# Reverse mapping for flexible lookup
UZ_TO_EN_PATHOLOGY = {v.lower(): k for k, v in PATHOLOGY_TRANSLATIONS_UZ.items()}
RU_TO_EN_PATHOLOGY = {v.lower(): k for k, v in PATHOLOGY_TRANSLATIONS_RU.items()}
for k, v in PATHOLOGY_TRANSLATIONS_UZ.items():
    UZ_TO_EN_PATHOLOGY[k.lower()] = k
for k, v in PATHOLOGY_TRANSLATIONS_RU.items():
    RU_TO_EN_PATHOLOGY[k.lower()] = k


def get_pathology_uz(name: str) -> str:
    """Return Uzbek translation for a pathology name."""
    if not name:
        return ""
    return PATHOLOGY_TRANSLATIONS_UZ.get(name, UZ_TO_EN_PATHOLOGY.get(name.lower(), name))


def get_pathology_ru(name: str) -> str:
    """Return Russian translation for a pathology name."""
    if not name:
        return ""
    return PATHOLOGY_TRANSLATIONS_RU.get(name, RU_TO_EN_PATHOLOGY.get(name.lower(), name))


def get_pathology_en(name: str) -> str:
    """Return English pathology identifier for a given English, Uzbek, or Russian pathology name."""
    if not name:
        return ""
    return UZ_TO_EN_PATHOLOGY.get(name.lower(), RU_TO_EN_PATHOLOGY.get(name.lower(), name))
