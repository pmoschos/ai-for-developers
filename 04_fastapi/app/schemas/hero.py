"""
Hero Schemas — Pydantic models for request/response contracts.

Separate from the SQLModel table so that:
  - HeroCreate: controls what the client sends
  - HeroUpdate: allows partial updates
  - HeroOut:    controls what the API returns
"""

from pydantic import BaseModel, Field


class HeroCreate(BaseModel):
    """Schema for creating a new hero."""
    name: str = Field(min_length=1, max_length=100)
    power: str = Field(min_length=1, max_length=100)
    age: int | None = Field(default=None, ge=0, le=1000)


class HeroUpdate(BaseModel):
    """Schema for partial hero updates. All fields optional."""
    name: str | None = None
    power: str | None = None
    age: int | None = None


class HeroOut(BaseModel):
    """Schema for hero responses."""
    id: int
    name: str
    power: str
    age: int | None = None
