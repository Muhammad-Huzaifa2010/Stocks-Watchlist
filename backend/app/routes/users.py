from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import User
from ..rate_limit import client_key, limiter
from ..schemas import TokenResponse, UserCreate, UserResponse
from ..security import (
    DUMMY_PASSWORD_HASH,
    create_access_token,
    hash_password,
    verify_password,
)


router = APIRouter()


@router.post("/users", response_model=UserResponse, status_code=201)
def create_user(
    user: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    limiter.check(
        client_key(request, "signup"),
        settings.signup_rate_limit,
        settings.rate_limit_window_seconds,
    )

    existing_email = (
        db.query(User)
        .filter(func.lower(User.email) == user.email)
        .first()
    )
    if existing_email:
        raise HTTPException(status_code=409, detail="Email already registered")

    existing_username = (
        db.query(User)
        .filter(func.lower(User.username) == user.username)
        .first()
    )
    if existing_username:
        raise HTTPException(status_code=409, detail="Username already exists")

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
    )
    db.add(new_user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Username or email already exists",
        )

    db.refresh(new_user)
    return new_user


@router.post(
    "/login",
    response_model=TokenResponse,
    description=(
        "Log in using your registered email address in the "
        "'username' field and your password."
    ),
)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    limiter.check(
        client_key(request, "login"),
        settings.login_rate_limit,
        settings.rate_limit_window_seconds,
    )

    email = form_data.username.strip().lower()

    email = form_data.username.strip().lower()
    user = db.query(User).filter(func.lower(User.email) == email).first()

    if user is None:
        verify_password(form_data.password, DUMMY_PASSWORD_HASH)
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
