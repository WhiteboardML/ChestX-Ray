from typing import Optional
from sqlalchemy.orm import Session
from backend.database.models import User


class UserRepository:

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """Fetch a user by email (case-insensitive)."""
        return db.query(User).filter(User.email == email.lower().strip()).first()

    @staticmethod
    def get_first(db: Session) -> Optional[User]:
        """Fetch the first user in the database (used for default demo login)."""
        return db.query(User).first()

    @staticmethod
    def add(db: Session, user: User) -> User:
        """Add a new user object to the session."""
        db.add(user)
        return user
