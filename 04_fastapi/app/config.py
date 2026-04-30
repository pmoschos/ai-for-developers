"""
Application Configuration — Typed Settings from .env

Uses pydantic-settings to read environment variables with types,
validation, and defaults. Cached with @lru_cache for a singleton.

Usage:
    from app.config import get_settings
    settings = get_settings()
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    All settings are read from environment variables or a .env file.
    Each field has a type and an optional default value.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",  # ignore extra env vars not defined here
    )

    # Database
    database_url: str = "sqlite:///./database.db"

    # JWT
    secret_key: str = "change-me-to-a-real-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (singleton)."""
    return Settings()
