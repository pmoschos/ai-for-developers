"""
02 — Path Parameters: Enum Constraints

Run:  uvicorn examples.02_parameters.enum_params:app --reload

Try:
  GET /users/admin   → 200 OK
  GET /users/hacker  → 422 (not a valid Role)
"""

# To run this code:
# fastapi dev enum_params.py
# or
# uvicorn enum_params:app --reload
# To view the Swagger UI documentation:
# http://localhost:8000/docs

from enum import Enum
from fastapi import FastAPI

# Create the FastAPI application instance.
# The title appears in the generated Swagger/OpenAPI docs.
app = FastAPI(
    title="Enum Path Parameters",
    description=(
        "Demonstrates how to validate path parameters using Enum. "
        "Only specific roles are accepted."
    ),
    version="1.0.0",
)


class Role(str, Enum):
    """
    Enum representing the only valid user roles accepted by the endpoint.

    Why inherit from both `str` and `Enum`?
    - `Enum` gives us a fixed set of allowed values.
    - `str` makes enum members behave like strings in many contexts,
      which is especially useful for JSON serialization and FastAPI docs.

    Allowed values:
    - admin
    - editor
    - viewer
    """
    admin = "admin"
    editor = "editor"
    viewer = "viewer"


@app.get("/users/{role}",summary="List users by role",
    description=(
        "Accepts only a valid role from the Role enum. "
        "If a value outside the enum is provided, FastAPI automatically "
        "returns a 422 validation error."
    ),
    tags=["Users"])
def list_users(role: Role):
    """
    FastAPI automatically validates the path parameter `role` against the `Role` enum.

    Behavior:
    - If the URL contains a value that matches one of the enum members (e.g., "admin",
      "editor", "viewer"), FastAPI converts it to the corresponding enum value and
      passes it to the function.
    - If the URL contains any other value (e.g., "guest", "hacker"), FastAPI automatically
      rejects the request with a 422 Unprocessable Entity response, and the endpoint
      function is never even called.

    This provides automatic type-checking and value validation at the HTTP layer,
    before the request even reaches your business logic.
    """
    return {"role": role, "message": f"Listing all {role.value}s"}
