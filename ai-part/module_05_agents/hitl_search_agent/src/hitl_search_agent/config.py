"""
hitl_search_agent.config
~~~~~~~~~~~~~~~~~~~~~~~~

Centralised environment configuration using pydantic-settings.

All settings are validated at startup. Missing required keys produce
clear, actionable error messages.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv


# ------------------------------------------------------------------
# Locate .env — project root is two levels above this file
# ------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_ENV_PATH = _PROJECT_ROOT / ".env"

# Force .env values to override system environment variables.
# pydantic-settings gives priority to system env vars by default,
# which causes stale system-level keys to shadow the .env file.
load_dotenv(dotenv_path=_ENV_PATH, override=True)


class Settings(BaseSettings):
    """
    Application settings, loaded from environment variables and/or
    a ``.env`` file at the project root.
    """

    # Required API keys
    openai_api_key: str
    tavily_api_key: str

    # Optional — LangSmith tracing
    langsmith_tracing: bool = False
    langsmith_api_key: str = ""
    langsmith_project: str = ""
    langsmith_endpoint: str = "https://api.smith.langchain.com"

    # Model settings
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.0

    # Tavily settings
    tavily_max_results: int = 5
    tavily_topic: str = "general"

    # Server settings
    server_host: str = "127.0.0.1"
    server_port: int = 7860

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=str(_ENV_PATH),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return the singleton Settings instance.

    Using ``lru_cache`` ensures the .env file is read exactly once
    and the same instance is reused everywhere.
    """
    return Settings()
