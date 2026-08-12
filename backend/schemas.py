from typing import List
from pydantic import BaseModel, Field


class PathologyScore(BaseModel):
    disease: str = Field(
        ...,
        description="Pathology/disease name as defined by TorchXRayVision",
        example="Pneumonia"
    )
    disease_uz: str = Field(
        ...,
        description="Pathology/disease name in Uzbek language",
        example="Pnevmoniya"
    )
    score: float = Field(
        ...,
        description="Raw model output score (unthresholded)",
        example=0.731
    )


class PredictResponse(BaseModel):
    model: str = Field(
        ...,
        description="Pretrained model identifier",
        example="densenet121-res224-all"
    )
    predictions: List[PathologyScore] = Field(
        ...,
        description="List of raw pathology scores ordered according to model.pathologies"
    )


class AnalyzeResponse(BaseModel):
    model: str = Field(
        ...,
        description="Pretrained model identifier",
        example="densenet121-res224-all"
    )
    pathologies: List[PathologyScore] = Field(
        ...,
        description="Complete list of raw pathology scores"
    )


class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status", example="ok")
    model: str = Field(..., description="Loaded model identifier", example="densenet121-res224-all")
    device: str = Field(..., description="Execution device (cuda or cpu)", example="cpu")


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error detail message", example="Invalid image file or format")


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

