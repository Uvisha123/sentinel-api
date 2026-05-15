from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/api_fortress_db"

    SECRET_KEY: str 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    SMTP_HOST: str = "sandbox.smtp.mailtrap.io"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""

    APP_ENV: str = "development"   # development | production
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"          # ignore unknown keys in .env


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance (loaded once at startup)."""
    return Settings()


# Convenience singleton — import this anywhere:  from app.config import settings
settings = get_settings()
