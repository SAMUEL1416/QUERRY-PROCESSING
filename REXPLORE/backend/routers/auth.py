"""
Authentication endpoints: register, login, logout, me.

Sessions are stateless JWT bearer tokens. The client stores the token and
sends it as `Authorization: Bearer <token>`. Logout simply confirms the
client should discard the token (there is no server-side session to void).
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import auth, models, schemas
from app.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=schemas.TokenOut, status_code=status.HTTP_201_CREATED)
def register(payload: schemas.RegisterRequest, db: Session = Depends(get_db)):
    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")

    normalized_email = auth.normalize_email(payload.email)

    existing = db.query(models.User).filter(models.User.email == normalized_email).first()
    if existing:
        raise HTTPException(status_code=409, detail="An account with this email already exists.")

    user = models.User(
        full_name=payload.full_name,
        email=normalized_email,
        password_hash=auth.hash_password(payload.password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    db.refresh(user)

    token = auth.create_access_token(user.id)
    return schemas.TokenOut(access_token=token, user=schemas.UserOut.model_validate(user))


@router.post("/login", response_model=schemas.TokenOut)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    normalized_email = auth.normalize_email(payload.email)
    user = db.query(models.User).filter(models.User.email == normalized_email).first()

    # Same generic message whether the email is unknown or the password is
    # wrong - never reveal which one was incorrect.
    invalid_credentials = HTTPException(status_code=401, detail="Invalid email or password.")

    if not user:
        raise invalid_credentials
    if not auth.verify_password(payload.password, user.password_hash):
        raise invalid_credentials

    token = auth.create_access_token(user.id)
    return schemas.TokenOut(access_token=token, user=schemas.UserOut.model_validate(user))


@router.post("/logout")
def logout(current_user: models.User = Depends(auth.get_current_user)):
    # Stateless JWTs: nothing to invalidate server-side. The frontend clears
    # the stored token. Requiring auth here also validates the token first.
    return {"detail": "Logged out."}


@router.get("/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user
