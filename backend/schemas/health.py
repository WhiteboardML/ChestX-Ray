from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status", example="ok")
    model: str = Field(..., description="Loaded model identifier", example="densenet121-res224-all")
    device: str = Field(..., description="Execution device (cuda or cpu)", example="cpu")
