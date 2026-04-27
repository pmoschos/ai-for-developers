"""
04 — Responses: Response Model Filtering

Run:  uvicorn examples.04_responses.response_model:app --reload

Try in /docs:
  POST /users → password is filtered OUT of the response
"""

from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

app = FastAPI(title="Response Models")


class UserIn(BaseModel):
    """What the client sends (includes password)."""
    username: str
    password: str
    email: EmailStr


class UserOut(BaseModel):
    """What the API returns (password stripped)."""
    username: str
    email: EmailStr


# In-memory storage for demo
users_db: list[dict] = []


@app.post("/users", response_model=UserOut)
def create_user(user: UserIn):
    """
    response_model=UserOut tells FastAPI to:
    1. Filter the response to only include fields in UserOut
    2. Document the response shape in OpenAPI
    3. The password is automatically excluded — a great safety net
    """
    users_db.append(user.model_dump())
    return user  # password is stripped from the response!
