"""
06 — Dependencies: Dependency Chains & Global Dependencies

This example demonstrates how FastAPI dependencies can depend on other
dependencies, forming a dependency chain.

Covered concepts:
1. Dependency chains
   One dependency can require the output of another dependency.

2. Header extraction and validation
   FastAPI can read values such as authentication tokens from headers.

3. Shared authentication logic
   Multiple endpoints can reuse the same authentication/user-resolution chain.

4. Per-request dependency caching
   If the same dependency result is needed multiple times during one request,
   FastAPI reuses it instead of recomputing it.

Run:
    uvicorn examples.06_dependencies.dependency_chain:app --reload

Alternative:
    fastapi dev dependency_chain.py

Open API docs:
    http://localhost:8000/docs

Try:
    GET /me
        without X-Token header
        -> 422 or 401 depending on the request and validation flow

    GET /me
        with header: X-Token: secret
        -> 200 OK
"""

from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException

# Create the FastAPI application instance.
# Its metadata appears in the generated Swagger/OpenAPI docs.
app = FastAPI(
    title="Dependency Chains",
    description=(
        "Demonstrates chained dependencies for token validation and "
        "current-user resolution in FastAPI."
    ),
    version="1.0.0",
)


def get_token(
    x_token: Annotated[
        str,
        Header(
            description="Authentication token sent in the X-Token header",
            examples=["secret"],
        ),
    ]
) -> str:
    """
    First dependency in the chain: extract and validate the token header.

    FastAPI reads `X-Token` from the incoming HTTP headers and injects it
    into this function as `x_token`.

    If the token is invalid, we raise an HTTPException and stop the chain.

    Example:
        X-Token: secret   -> valid
        X-Token: wrong    -> invalid
    """
    if x_token != "secret":
        raise HTTPException(status_code=401, detail="Invalid token")
    return x_token


def get_current_user(token: Annotated[str, Depends(get_token)]) -> dict:
    """
    Second dependency in the chain: resolve the current user.

    This dependency depends on `get_token`, so FastAPI runs `get_token` first.
    If token validation succeeds, the validated token is passed here.

    In a real application, this step might:
    - decode a JWT
    - query a database
    - check permissions
    - load a user profile

    For this demo, we simply return a fake user dictionary.
    """
    return {
        "username": "alice",
        "token": token,
    }


# Reusable alias for cleaner endpoint signatures.
CurrentUser = Annotated[dict, Depends(get_current_user)]


@app.get(
    "/me",
    summary="Return the current authenticated user",
    description=(
        "Uses a dependency chain to validate the X-Token header and resolve "
        "the current user before the endpoint runs."
    ),
    tags=["Auth"],
)
def me(user: CurrentUser):
    """
    Return the authenticated user.

    Dependency resolution order:
        get_token -> get_current_user -> endpoint

    If any dependency in the chain fails, the endpoint itself does not run.

    This pattern is very common for:
    - authentication
    - authorization
    - tenant resolution
    - session/user loading
    """
    return user


@app.get(
    "/admin",
    summary="Admin endpoint reusing the same dependency chain",
    description=(
        "Reuses the same current-user dependency chain as /me. "
        "This demonstrates how authentication logic can be centralized "
        "and shared across multiple endpoints."
    ),
    tags=["Auth"],
)
def admin(user: CurrentUser):
    """
    Return a message for the authenticated admin user.

    The key point here is reuse:
    both `/me` and `/admin` depend on the same user-resolution chain,
    so the authentication logic is written once and reused safely.
    """
    return {"message": f"Welcome admin {user['username']}"}