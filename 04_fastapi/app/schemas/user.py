"""
User Schemas — Pydantic models for request/response contracts.
"""

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """Schema for user registration."""
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)


class UserOut(BaseModel):
    """Schema for user responses (password excluded)."""
    id: int
    username: str
    is_admin: bool
