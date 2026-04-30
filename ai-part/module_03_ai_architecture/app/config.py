"""
Configuration Management
========================
Centralized configuration for the AI API.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment"""
    
    # API Keys
    openai_api_key: str = ""
    anthropic_api_key: Optional[str] = None
    
    # Model Configuration
    default_model: str = "gpt-4o-mini"
    max_tokens_default: int = 500
    temperature_default: float = 0.7
    
    # Rate Limiting
    rate_limit_requests: int = 60  # requests per minute
    rate_limit_tokens: int = 100000  # tokens per minute
    
    # Retry Configuration
    max_retries: int = 3
    retry_min_wait: float = 1.0
    retry_max_wait: float = 10.0
    
    # Timeout
    request_timeout: float = 30.0
    
    # Logging
    log_level: str = "INFO"
    
    # Cost Tracking
    track_costs: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Model pricing (per 1M tokens)
MODEL_PRICING = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
}


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Estimate cost for a request"""
    pricing = MODEL_PRICING.get(model, MODEL_PRICING["gpt-4o-mini"])
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    return input_cost + output_cost
