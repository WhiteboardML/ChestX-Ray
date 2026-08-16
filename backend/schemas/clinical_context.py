from pydantic import BaseModel
from typing import List, Optional

class ClinicalContext(BaseModel):
    symptoms: List[str] = []
    temperature: Optional[float] = None
    spo2: Optional[int] = None
    crp_level: Optional[float] = None  # C-Reactive Protein (mg/L)
    wbc_count: Optional[float] = None  # White Blood Cell count (x10^9/L)
