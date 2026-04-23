"""
02 — Path Parameters with Response Models

This example demonstrates two FastAPI path parameter patterns and shows
how to document the returned JSON structure using Pydantic response models.

Covered concepts:
1. Typed path parameters
   - FastAPI validates and converts values based on Python type hints.
2. Catch-all path parameters with :path
   - Useful when the parameter must include slashes.
3. response_model
   - Documents and validates the shape of the response.

Run:
    uvicorn path_params_response_models:app --reload

Alternative:
    fastapi dev path_params_response_models.py

Open API docs:
    http://localhost:8000/docs

Try:
    GET /users/42
        -> {"user_id": 42, "kind": "int"}

    GET /users/abc
        -> 422 Unprocessable Entity

    GET /files/report.txt
        -> {"file_path": "report.txt", "kind": "str"}

    GET /files/home/user/data.csv
        -> {"file_path": "home/user/data.csv", "kind": "str"}
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field

# Create the FastAPI application instance.
# Its title, description, and version are displayed in Swagger/OpenAPI docs.
app = FastAPI(
    title="Path Parameters",
    description=(
        "Demonstrates typed path parameters, catch-all path parameters, "
        "and response models with Pydantic."
    ),
    version="1.0.0",
)


class UserResponse(BaseModel):
    """
    Response schema for the /users/{user_id} endpoint.

    Fields:
    - user_id: the validated integer extracted from the URL
    - kind: the runtime Python type name of user_id
    """
    user_id: int = Field(..., description="The validated numeric user ID")
    kind: str = Field(..., description="The runtime Python type of user_id")


class FileResponse(BaseModel):
    """
    Response schema for the /files/{file_path:path} endpoint.

    Fields:
    - file_path: the path captured from the URL
    - kind: the runtime Python type name of file_path
    """
    file_path: str
    kind: str


@app.get(
    "/users/{user_id}",
    response_model=UserResponse,
    tags=["Users"],
    summary="Get a user by numeric ID",
    description=(
        "Accepts a user ID as a path parameter. FastAPI validates that "
        "the provided value is an integer and converts it automatically."
    ),
)
def get_user(user_id: int):
    """
    Return a validated numeric user ID.

    The `user_id: int` annotation tells FastAPI to:
    1. read the value from the URL,
    2. validate that it is a valid integer,
    3. convert it from string to int automatically,
    4. return a 422 error if validation fails.

    Example:
        /users/42   -> valid
        /users/abc  -> invalid
    """
    return UserResponse(
        user_id=user_id,
        kind=type(user_id).__name__,
    )


@app.get(
    "/files/{file_path:path}",
    response_model=FileResponse,
    tags=["Files"],
    summary="Read a file path from the URL",
    description=(
        "Uses the special :path converter to capture the entire remaining "
        "part of the URL, including slashes."
    ),
)
def read_file(file_path: str):
    """
    Return the full file path captured from the URL.

    Normally, a path parameter stops at the next slash (/).
    By using `{file_path:path}`, FastAPI captures the rest of the path
    as a single string.

    Example:
        /files/report.txt
            -> file_path = 'report.txt'

        /files/home/user/data.csv
            -> file_path = 'home/user/data.csv'
    """
    return FileResponse(
        file_path=file_path,
        kind=type(file_path).__name__,
    )