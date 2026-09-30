from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    database_url: str
    secret_key: str = Field(min_length=32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    cors_origins: str = (
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:5174,http://127.0.0.1:5174"
    )
    login_rate_limit: int = 5
    signup_rate_limit: int = 3
    rate_limit_window_seconds: int = 60

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("algorithm")
    @classmethod
    def algorithm_must_be_hs256(cls, value: str) -> str:
        if value != "HS256":
            raise ValueError("ALGORITHM must be HS256")
        return value

    @field_validator("secret_key")
    @classmethod
    def secret_key_must_not_be_placeholder(cls, value: str) -> str:
        if value.strip() in {"", "your_secret_key_here", "changeme"}:
            raise ValueError("SECRET_KEY must be set to a unique secret")
        return value

    def parsed_cors_origins(self) -> list[str]:
        origins = [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]
        if any(origin == "*" for origin in origins):
            raise ValueError(
                "Wildcard CORS origins are not allowed with credentialed requests"
            )
        return origins


settings = Settings()
