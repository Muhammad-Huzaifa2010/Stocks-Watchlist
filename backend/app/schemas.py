import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


USERNAME_PATTERN = re.compile(r"^[a-z0-9._-]+$")
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9.-]+$")


def _blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


class StockCreate(BaseModel):
    symbol: str = Field(min_length=1, max_length=10)
    company_name: str = Field(min_length=1, max_length=100)
    market: str = Field(min_length=1, max_length=50)
    sector: str | None = Field(default=None, max_length=100)
    notes: str | None = Field(default=None, max_length=500)

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        symbol = value.strip().upper()
        if not symbol:
            raise ValueError("Symbol is required")
        if not SYMBOL_PATTERN.fullmatch(symbol):
            raise ValueError(
                "Symbol may only contain letters, numbers, periods, and hyphens"
            )
        return symbol

    @field_validator("company_name", "market")
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError("This field is required")
        return text

    @field_validator("sector", "notes")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _blank_to_none(value)


class StockResponse(BaseModel):
    id: int
    symbol: str
    company_name: str
    market: str
    sector: str | None
    notes: str | None

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(min_length=8)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        username = value.strip().lower()
        if len(username) < 3 or len(username) > 30:
            raise ValueError("Username must be between 3 and 30 characters")
        if not USERNAME_PATTERN.fullmatch(username):
            raise ValueError(
                "Username may only contain lowercase letters, numbers, "
                "underscores, periods, and hyphens"
            )
        return username

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()

    @field_validator("password")
    @classmethod
    def max_72_bytes(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 bytes")
        return value


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str

