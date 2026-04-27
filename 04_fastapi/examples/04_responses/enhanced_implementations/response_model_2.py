"""
04 — Responses: Response Model Filtering

This example demonstrates one of the most useful FastAPI features:
using a response model to control what data is returned to the client.

Covered concepts:
1. Separate input and output schemas
   - `UserIn` describes what the client sends
   - `UserOut` describes what the API returns

2. Response filtering
   - Even if the returned object contains extra fields,
     FastAPI keeps only the fields declared in `response_model`

3. Basic safety pattern
   - Sensitive data such as passwords should not be returned in responses

4. OpenAPI documentation
   - The response schema shown in Swagger is based on `UserOut`

Run:
    uvicorn examples.04_responses.response_model:app --reload

Alternative:
    fastapi dev response_model.py

Open API docs:
    http://localhost:8000/docs

Try in /docs:
    POST /users
    with body:
    {
        "username": "john_doe",
        "password": "supersecret123",
        "email": "john@example.com"
    }

Expected result:
    The password is accepted in the request,
    but filtered out of the response.
"""

from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, Field

# Create the FastAPI application instance.
# Its metadata appears in the generated Swagger/OpenAPI docs.
app = FastAPI(
    title="Response Models",
    description=(
        "Demonstrates how response_model filters outgoing data and helps "
        "separate input schemas from output schemas."
    ),
    version="1.0.0",
)


class UserIn(BaseModel):
    """
    Schema representing the JSON body sent by the client.

    This is the input model.
    It includes all fields required for user creation,
    including sensitive data such as the password.
    """
    username: str = Field(..., description="The user's public username", examples=["john_doe"])
    password: str = Field(..., description="The user's password", examples=["supersecret123"])
    email: EmailStr = Field(..., description="The user's email address", examples=["john@example.com"])


class UserOut(BaseModel):
    """
    Schema representing the JSON returned by the API.

    This is the output model.
    Notice that it intentionally excludes the password field.
    """
    username: str = Field(..., description="The user's public username", examples=["john_doe"])
    email: EmailStr = Field(..., description="The user's email address", examples=["john@example.com"])


# In-memory storage for demonstration only.
# In a real application, this would usually be a database.
users_db: list[dict] = []


@app.post(
    "/users",
    response_model=UserOut,
    summary="Create a user and filter sensitive fields from the response",
    description=(
        "Accepts a request body matching UserIn, stores it, and returns a "
        "response matching UserOut. Fields not present in UserOut, such as "
        "the password, are automatically excluded from the response."
    ),
    tags=["Users"],
)
def create_user(user: UserIn):
    """
    Create a user from the request body.

    Important behavior:
    `response_model=UserOut` tells FastAPI to validate and filter the
    outgoing response so that only `username` and `email` are returned.

    This means:
    1. the client may send a password,
    2. the application may temporarily work with that password,
    3. but the password is not exposed in the final JSON response.

    This is a very common and important API design pattern:
    - input model for incoming data
    - output model for safe returned data

    Example request body:
        {
            "username": "john_doe",
            "password": "supersecret123",
            "email": "john@example.com"
        }

    Example response body:
        {
            "username": "john_doe",
            "email": "john@example.com"
        }
    """
    users_db.append(user.model_dump())

    # We intentionally return the full user object here.
    # FastAPI will filter the response using UserOut.
    return user

# get all users but the response must be a list of UserOut objects
@app.get(
        "/users",
        response_model=list[UserOut],
        summary="Get all users and filter sensitive fields from the response",
        description=(
            "Returns a list of UserOut objects. Fields not present in UserOut, such as "
            "the password, are automatically excluded from the response."
        ),
        tags=["Users"],
    )
def get_all_users():
    """
    Get all users from the in-memory storage.

    Important behavior:
    `response_model=list[UserOut]` tells FastAPI to validate and filter the
    outgoing response so that only `username` and `email` are returned for
    each user.

    This means:
    1. each item in the returned list matches the UserOut schema,
    2. sensitive data such as the password is not exposed in the response,
    3. the response is a JSON array of user objects.
    """
    return users_db
