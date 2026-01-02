from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ScanCreate(BaseModel):
    patient_name: str
    patient_id: Optional[str] = None
    notes: Optional[str] = None

class ScanRead(BaseModel):
    id: int
    patient_name: str
    patient_id: Optional[str] = None
    prediction: str
    confidence: float
    all_probabilities: Optional[str] = None
    notes: Optional[str] = None
    screened_by: Optional[str] = None
    status: str
    image_data: Optional[str] = None
    scan_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class ScanUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

class AnalyticsResponse(BaseModel):
    total_scans: int
    abnormal_percentage: float
    condition_distribution: dict
    daily_scans: dict
