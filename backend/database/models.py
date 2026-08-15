from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime

from backend.database.connection import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(String, primary_key=True, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    name = Column(String, nullable=False, index=True)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    phone = Column(String, nullable=True, default="+998 90 123-45-67")
    medical_status = Column(String, nullable=True, default="Nazoratda")
    created_at = Column(String, nullable=True)
    status = Column(String, nullable=True, default="Kutilmoqda")
    diagnosis = Column(String, nullable=True, default="Tahlil kutilmoqda")
    probability = Column(Float, nullable=True, default=0.0)

    # Relationships
    scans = relationship("Scan", back_populates="patient", cascade="all, delete-orphan", order_by="desc(Scan.id)")


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    scan_id = Column(String, index=True, nullable=False)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False, index=True)
    timestamp = Column(String, nullable=False)
    diagnosis = Column(String, nullable=False)
    diagnosis_eng = Column(String, nullable=False)
    probability = Column(Float, nullable=False)
    urgency = Column(JSON, nullable=True)
    original_image = Column(String, nullable=False)
    heatmap_image = Column(String, nullable=False)
    status = Column(String, nullable=False, default="Ko'rik kutilmoqda")
    approved_by = Column(String, nullable=True)
    approved_time = Column(String, nullable=True)
    raw_scores = Column(JSON, nullable=False)
    findings = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    # Relationship
    patient = relationship("Patient", back_populates="scans")


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="Doctor")
    is_subscribed = Column(Integer, default=0)  # 1 = Subscribed, 0 = Unpaid
    plan_name = Column(String, default="None")  # "SaaS Obunasi", "Token-based", "None"
    scan_tokens = Column(Integer, default=0)
    card_number = Column(String, default="4916 9903 3783 3237")
    created_at = Column(String, nullable=True)
