from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .models import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

MAX_USER_ID = 2_147_483_647
MAX_PASSWORD_BYTES = 72

# Precomputed bcrypt hash used only to keep unknown-email login timing similar
# to a real password check. It does not correspond to any user account.
DUMMY_PASSWORD_HASH = (
    "$2b$12$muk1OlPH3es2nBWRCsXaEuU/GZZi2ignpSpbbinjAga6UERlV1ESi"
)


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > MAX_PASSWORD_BYTES:
        raise ValueError("Password must be at most 72 bytes")

    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        password_bytes = password.encode("utf-8")
        if len(password_bytes) > MAX_PASSWORD_BYTES:
            return False
        return bcrypt.checkpw(password_bytes, hashed_password.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def get_user_id_from_subject(subject: object) -> int | None:
    if not isinstance(subject, str):
        return None
    if not (subject.isascii() and subject.isdigit()):
        return None

    user_id = int(subject)
    if user_id < 1 or user_id > MAX_USER_ID:
        return None
    return user_id


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
            options={"require_exp": True, "require_sub": True},
        )
    except (JWTError, TypeError, ValueError):
        raise credentials_exception

    user_id = get_user_id_from_subject(payload.get("sub"))
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user
