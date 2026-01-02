from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from asess.core.database import Base
from datetime import datetime

class ScanResult(Base):
    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String, nullable=False)
    patient_id = Column(String, nullable=True)
    prediction = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    all_probabilities = Column(Text, nullable=True)  # JSON string of all class probabilities
    notes = Column(Text, nullable=True)
    screened_by = Column(String, nullable=True)
    status = Column(String, default="Pending Review")  # "Pending Review", "Verified"
    image_data = Column(Text, nullable=True)  # base64 image data
    scan_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
