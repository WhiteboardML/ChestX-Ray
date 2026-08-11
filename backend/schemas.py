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
