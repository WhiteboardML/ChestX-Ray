from typing import List, Optional
from sqlalchemy.orm import Session
from backend.database.models import Scan


class ScanRepository:

    @staticmethod
    def get_by_id(db: Session, scan_id: str) -> Optional[Scan]:
        """Fetch a single scan by scan_id string."""
        return db.query(Scan).filter(Scan.scan_id == scan_id).first()

    @staticmethod
    def get_all_sorted_desc(db: Session) -> List[Scan]:
        """Fetch all scans sorted by ID descending (newest first)."""
        return db.query(Scan).order_by(Scan.id.desc()).all()

    @staticmethod
    def add(db: Session, scan: Scan) -> Scan:
        """Add a new scan object to the session."""
        db.add(scan)
        return scan
