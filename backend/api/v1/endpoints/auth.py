import uuid
import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.database.connection import get_db
from backend.database.models import User
from backend.repositories.user_repository import UserRepository
from backend.services.mappers import user_to_dict

router = APIRouter()

RECEIVING_CARD_NUMBER = "4916 9903 3783 3237"


class RegisterRequest(BaseModel):
    email: str
    username: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class SubscribeRequest(BaseModel):
    email: Optional[str] = "dr.karimov@clinic.uz"
    plan_type: str  # 'saas' | 'token' | 'university'
    card_number: Optional[str] = None


@router.post("/api/auth/register")
async def register_user(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = UserRepository.get_by_email(db, req.email)
    if existing:
        raise HTTPException(status_code=400, detail="Ushbu email bilan foydalanuvchi allaqachon mavjud.")

    user_id = f"USR-{uuid.uuid4().hex[:6].upper()}"
    new_user = User(
        id=user_id,
        email=req.email.lower().strip(),
        username=req.username.strip(),
        password_hash=req.password,
        role="Doctor",
        is_subscribed=1,          # Unlimited access by default
        plan_name="SaaS Obunasi (Cheksiz)",
        scan_tokens=99999,
        card_number=None,
        created_at=datetime.datetime.now().strftime("%Y-%m-%d")
    )
    UserRepository.add(db, new_user)
    db.commit()
    db.refresh(new_user)
    return user_to_dict(new_user)


@router.post("/api/auth/login")
async def login_user(req: LoginRequest, db: Session = Depends(get_db)):
    user = UserRepository.get_by_email(db, req.email)
    if not user or user.password_hash != req.password:
        raise HTTPException(status_code=401, detail="Email yoki parol noto'g'ri.")
    return user_to_dict(user)


@router.post("/api/auth/subscribe")
async def subscribe_user(req: SubscribeRequest, db: Session = Depends(get_db)):
    target_email = (req.email or "dr.karimov@clinic.uz").lower().strip()
    user = UserRepository.get_by_email(db, target_email)
    if not user:
        user = UserRepository.get_first(db)
    if not user:
        user_id = f"USR-{uuid.uuid4().hex[:6].upper()}"
        user = User(
            id=user_id,
            email=target_email,
            username="Dr. Karimov",
            password_hash="demo123",
            role="Pulmonolog",
            is_subscribed=1,
            plan_name="SaaS Obunasi",
            scan_tokens=99999,
            card_number=RECEIVING_CARD_NUMBER,
            created_at=datetime.datetime.now().strftime("%Y-%m-%d")
        )
        UserRepository.add(db, user)
        db.flush()

    if req.plan_type == 'saas':
        user.is_subscribed = 1
        user.plan_name = "SaaS Obunasi (Eng ommabop)"
        user.scan_tokens = 99999
    elif req.plan_type == 'token':
        user.is_subscribed = 1
        user.plan_name = "Token-based to'lov"
        user.scan_tokens += 100
    elif req.plan_type == 'university':
        user.is_subscribed = 1
        user.plan_name = "Universitet / Tadqiqot Litsenziyasi"
        user.scan_tokens += 500

    user.card_number = RECEIVING_CARD_NUMBER
    db.commit()
    db.refresh(user)
    return user_to_dict(user)


@router.get("/api/auth/me")
async def get_current_user_profile(email: Optional[str] = None, db: Session = Depends(get_db)):
    if email:
        user = UserRepository.get_by_email(db, email)
        if user:
            return user_to_dict(user)
    default_user = UserRepository.get_first(db)
    if not default_user:
        default_user = User(
            id="USR-DR-KARIMOV",
            email="dr.karimov@clinic.uz",
            username="Dr. Karimov",
            password_hash="demo123",
            role="Pulmonolog",
            is_subscribed=1,
            plan_name="SaaS Obunasi",
            scan_tokens=99999,
            card_number=RECEIVING_CARD_NUMBER,
            created_at=datetime.datetime.now().strftime("%Y-%m-%d")
        )
        UserRepository.add(db, default_user)
        db.commit()
        db.refresh(default_user)
    return user_to_dict(default_user)
