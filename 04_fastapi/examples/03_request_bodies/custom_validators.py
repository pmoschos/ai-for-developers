"""
03 — Request Bodies: Custom Validators

Run:  uvicorn examples.03_request_bodies.custom_validators:app --reload

Try in /docs:
  POST /signup with mismatched passwords → validation error
"""

from fastapi import FastAPI
from pydantic import BaseModel, field_validator, model_validator

app = FastAPI(title="Custom Validators")


class SignupData(BaseModel):
    username: str
    password: str
    password_confirm: str

    @field_validator("password")
    @classmethod
    def strong_password(cls, v: str) -> str:
        """Validate a single field: password strength."""
        if len(v) < 8 or v.isalpha():
            raise ValueError("Password must be 8+ chars and include non-letters")
        return v

    @model_validator(mode="after")
    def passwords_match(self):
        """Validate across fields: passwords must match."""
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self


@app.post("/signup")
def signup(data: SignupData):
    """
    Custom validators run automatically during Pydantic validation.
    - @field_validator: validates a single field
    - @model_validator: validates across multiple fields
    """
    return {"ok": True, "username": data.username}
