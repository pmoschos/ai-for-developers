"""
03 — Request Bodies: Field-Level Validation

This example demonstrates how to validate individual model fields
using Pydantic's Field(...) and specialized types such as EmailStr.

Covered concepts:
1. Field-level validation
   - minimum and maximum string length
   - regex/pattern matching
   - numeric ranges

2. Specialized field types
   - EmailStr validates email format

3. Optional fields
   - fields with a default of None are optional

4. Automatic API documentation
   - descriptions and examples appear in Swagger/OpenAPI docs

Run:
    uvicorn examples.03_request_bodies.field_validation:app --reload

Alternative:
    fastapi dev field_validation.py

Open API docs:
    http://localhost:8000/docs

Try in /docs:
    POST /users
    with body:
    {
        "username": "ab",
        "email": "me@x.com",
        "age": 20
    }

Expected result:
    422 Unprocessable Entity
    because username must be at least 3 characters long.
"""

from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, Field

# Create the FastAPI application instance.
# Its metadata is shown in the generated Swagger/OpenAPI docs.
app = FastAPI(
    title="Field Validation",
    description=(
        "Demonstrates field-level validation for JSON request bodies "
        "using Pydantic Field(...) constraints."
    ),
    version="1.0.0",
)


# To run this code:
# fastapi dev field_validation.py
# or
# uvicorn field_validation:app --reload
# To view the Swagger UI documentation:
# http://localhost:8000/docs

class UserCreate(BaseModel):
    """
    Pydantic model representing the expected JSON body for user creation.

    Validation rules:
    - username:
        * 3 to 20 characters
        * lowercase letters, digits, and underscores only
    - email:
        * must be a valid email address
    - age:
        * must be between 13 and 120
    - bio:
        * optional
        * maximum 280 characters

    FastAPI uses this model to validate incoming JSON automatically.
    """
    username: str = Field(
        ...,
        min_length=3,
        max_length=20,
        pattern=r"^[a-z0-9_]+$",
        description="Lowercase letters, numbers, and underscores only",
        examples=["john_doe"],
    )
    email: EmailStr = Field(
        ...,
        description="A valid email address",
        examples=["me@example.com"],
    )
    age: int = Field(
        ...,
        ge=13,
        le=120,
        description="Must be between 13 and 120",
        examples=[20],
    )
    bio: str | None = Field(
        default=None,
        max_length=280,
        description="Optional short biography with a maximum of 280 characters",
        examples=["Python developer and coffee enthusiast."],
    )


@app.post(
    "/users",
    summary="Create a user with validated fields",
    description=(
        "Accepts a JSON request body matching the UserCreate model. "
        "Pydantic validates each field automatically and FastAPI returns "
        "a 422 response if any rule is violated."
    ),
    tags=["Users"],
)
def create_user(user: UserCreate):
    """
    Create a user after field-level validation succeeds.

    Validation examples:
    - username too short -> rejected
    - username with uppercase letters or spaces -> rejected
    - invalid email format -> rejected
    - age outside the allowed range -> rejected
    - bio longer than 280 characters -> rejected

    Example valid body:
        {
            "username": "john_doe",
            "email": "john@example.com",
            "age": 25,
            "bio": "Backend developer"
        }
    """
    return {
        "ok": True,
        "user": user.model_dump(),
        "types": {
            "username": type(user.username).__name__,
            "email": type(user.email).__name__,
            "age": type(user.age).__name__,
            "bio": type(user.bio).__name__ if user.bio is not None else None,
        },
    }
