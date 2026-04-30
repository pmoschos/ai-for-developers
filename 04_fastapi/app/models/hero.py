"""
Hero Model — SQLModel table definition.
"""

from sqlmodel import Field, SQLModel


class Hero(SQLModel, table=True):
    """A hero stored in the database."""
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    power: str
    age: int | None = None
