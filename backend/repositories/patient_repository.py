from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, desc
from backend.database.models import Patient


class PatientRepository:

    @staticmethod
    def get_by_id(db: Session, patient_id: str) -> Optional[Patient]:
        """Fetch a single patient profile by ID."""
        return db.query(Patient).filter(Patient.id == patient_id).first()

    @staticmethod
    def get_by_names(db: Session, first_name: str, last_name: str) -> Optional[Patient]:
        """Fetch a patient profile by first and last name match (case-insensitive)."""
        return db.query(Patient).filter(
            func.lower(Patient.first_name) == first_name.lower(),
            func.lower(Patient.last_name) == last_name.lower()
        ).first()

    @staticmethod
    def get_by_full_name(db: Session, name: str) -> Optional[Patient]:
        """Fetch a patient profile by full name match (case-insensitive)."""
        return db.query(Patient).filter(
            func.lower(Patient.name) == name.lower()
        ).first()

    @staticmethod
    def get_all(db: Session) -> List[Patient]:
        """Fetch all patient profiles."""
        return db.query(Patient).all()

    @staticmethod
    def get_recent(db: Session, limit: int = 10) -> List[Patient]:
        """Fetch recently added patients sorted by ID descending."""
        return db.query(Patient).order_by(desc(Patient.id)).limit(limit).all()

    @staticmethod
    def search(db: Session, query_str: str) -> List[Patient]:
        """Search patients by name, first name, last name, or ID."""
        q_clean = query_str.strip().lower()
        if not q_clean:
            return PatientRepository.get_recent(db)
        return db.query(Patient).filter(
            or_(
                func.lower(Patient.name).contains(q_clean),
                func.lower(Patient.first_name).contains(q_clean),
                func.lower(Patient.last_name).contains(q_clean),
                func.lower(Patient.id).contains(q_clean)
            )
        ).order_by(desc(Patient.id)).all()

    @staticmethod
    def count(db: Session) -> int:
        """Get the total count of patients in the database."""
        return db.query(Patient).count()

    @staticmethod
    def add(db: Session, patient: Patient) -> Patient:
        """Add a new patient to the session."""
        db.add(patient)
        return patient
