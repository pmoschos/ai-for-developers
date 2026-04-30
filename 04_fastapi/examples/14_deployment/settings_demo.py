"""
14 — Deployment: Settings with Environment Variables

Run:
    uvicorn settings_demo:app --reload

What this file teaches:
    - How to use pydantic-settings to load config from environment variables
    - How to use a .env file for local development
    - How to set sensible defaults that can be overridden in production
    - How to disable /docs in production for security
    - How to use @lru_cache for efficient settings access

Key idea:
    Never hardcode secrets or configuration in your source code.
    Use environment variables that can be set differently in each
    environment (development, staging, production).

    pydantic-settings automatically reads from:
    1. Environment variables (highest priority)
    2. A .env file (for local development convenience)
    3. Default values in the class (lowest priority)
"""

import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi import Depends, FastAPI


# ============================================================================
# Settings Class
# ============================================================================

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    pydantic-settings will:
    - read from environment variables (case-insensitive)
    - read from a .env file if one exists
    - use the default values defined here as fallbacks

    In production, set these via environment variables:
        export SECRET_KEY="your-production-secret"
        export DATABASE_URL="postgresql://..."
        export DEBUG=false
    """

    # Application metadata
    app_name: str = "FastAPI App"
    debug: bool = True

    # Security
    secret_key: str = "dev-only-secret-change-me"
    access_token_expire_minutes: int = 30

    # Database
    database_url: str = "sqlite:///./database.db"

    # CORS
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    # Pydantic-settings configuration.
    # env_file tells it to read from a .env file in the current directory.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Return a cached Settings instance.

    @lru_cache ensures the settings are only loaded once,
    even though get_settings() is called on every request
    when used as a dependency.

    This is the recommended pattern from the FastAPI docs.
    """
    return Settings()


# ============================================================================
# App — configured from settings
# ============================================================================

settings = get_settings()

# Conditionally disable Swagger UI in production.
# This prevents exposing your API schema to the public.
docs_url = "/docs" if settings.debug else None
redoc_url = "/redoc" if settings.debug else None

app = FastAPI(
    title=settings.app_name,
    docs_url=docs_url,
    redoc_url=redoc_url,
)


@app.get("/")
def root():
    return {
        "app": settings.app_name,
        "debug": settings.debug,
        "docs": docs_url,
    }


@app.get("/settings")
def show_settings(current_settings: Settings = Depends(get_settings)):
    """
    Show non-secret settings.

    In a real app, NEVER expose secrets in an endpoint.
    This is just for demonstration.

    Using Depends(get_settings) makes the settings injectable
    and overridable in tests.
    """
    return {
        "app_name": current_settings.app_name,
        "debug": current_settings.debug,
        "database_url": current_settings.database_url,
        "token_expire_minutes": current_settings.access_token_expire_minutes,
        "cors_origins": current_settings.cors_origins,
        # Intentionally NOT exposing secret_key
    }
