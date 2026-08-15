from typing import List
from pydantic import BaseModel
from backend.schemas.inference import PathologyScore


class PatientScan(BaseModel):
    scan_id: str
    timestamp: str
    diagnosis: str
    diagnosis_eng: str
    probability: float
    original_image: str
    heatmap_image: str
    status: str
    approved_by: str = None
    approved_time: str = None
    raw_scores: List[PathologyScore] = []
    findings: dict = {}


class PatientProfile(BaseModel):
    id: str
    first_name: str
    last_name: str
    name: str
    age: int
    gender: str
    created_at: str
    scans: List[PatientScan] = []


class PatientSearchResult(BaseModel):
    id: str
    name: str
    age: int
    gender: str
    scan_count: int
    last_diagnosis: str
    last_scan_time: str
