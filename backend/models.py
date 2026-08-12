"""
SQLAlchemy ORM Data Models for Patients, Scans, AI Predictions, and Findings.
"""
from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime

from backend.database import Base


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

    def to_dict(self):
        """Convert Patient model to dictionary structure."""
        scans_list = [scan.to_dict() for scan in self.scans] if self.scans else []
        latest_scan = self.scans[0] if self.scans else None

        return {
            "id": self.id,
            "first_name": self.first_name or "",
            "last_name": self.last_name or "",
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "phone": self.phone or "+998 90 123-45-67",
            "medical_status": self.medical_status or "Nazoratda",
            "created_at": self.created_at or datetime.datetime.now().strftime("%Y-%m-%d"),
            "status": self.status or "Kutilmoqda",
            "diagnosis": self.diagnosis or "Norma",
            "probability": self.probability or 0.0,
            "upload_time": latest_scan.timestamp if latest_scan else self.created_at,
            "original_image": latest_scan.original_image if latest_scan else None,
            "heatmap_image": latest_scan.heatmap_image if latest_scan else None,
            "approved_by": self.status == "Tasdiqlangan" and (latest_scan.approved_by if latest_scan else None) or None,
            "approved_time": latest_scan.approved_time if latest_scan else None,
            "raw_scores": latest_scan.raw_scores if latest_scan else [],
            "findings": latest_scan.findings if latest_scan else {
                "summary": "Bemor profil yaratildi.",
                "simple_lang": "Rentgen tahlilini o'tkazish uchun yangi fayl yuklang.",
                "precautions": ["Bemor holatini kuzatib boring."],
                "technical": "Profile created."
            },
            "urgency": latest_scan.urgency if latest_scan else None,
            "scans": scans_list
        }


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

    def to_dict(self):
        """Convert Scan model to dictionary structure."""
        return {
            "id": self.id,
            "scan_id": self.scan_id,
            "patient_id": self.patient_id,
            "patient_name": self.patient.name if self.patient else "",
            "patient_age": self.patient.age if self.patient else 0,
            "patient_gender": self.patient.gender if self.patient else "",
            "patient_phone": self.patient.phone if self.patient else "+998 90 123-45-67",
            "timestamp": self.timestamp,
            "diagnosis": self.diagnosis,
            "diagnosis_eng": self.diagnosis_eng,
            "probability": self.probability,
            "urgency": self.urgency,
            "original_image": self.original_image,
            "heatmap_image": self.heatmap_image,
            "status": self.status,
            "approved_by": self.approved_by,
            "approved_time": self.approved_time,
        }


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

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "role": self.role,
            "is_subscribed": bool(self.is_subscribed),
            "plan_name": self.plan_name,
            "scan_tokens": self.scan_tokens,
            "card_number": self.card_number,
            "created_at": self.created_at
        }
