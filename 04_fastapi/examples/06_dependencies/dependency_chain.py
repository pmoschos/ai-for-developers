"""
06 — Dependencies: Dependency Chains & Global Dependencies

Run:  uvicorn examples.06_dependencies.dependency_chain:app --reload

Try:
  GET /me  without X-Token header → 401
  GET /me  with X-Token: secret   → 200
"""

from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException

app = FastAPI(title="Dependency Chains")


# --- Dependency 1: verify token ---
def get_token(x_token: Annotated[str, Header()]) -> str:
    """First link in the chain: validate the token header."""
    if x_token != "secret":
        raise HTTPException(401, "Invalid token")
    return x_token


# --- Dependency 2: depends on Dependency 1 ---
def get_current_user(token: Annotated[str, Depends(get_token)]) -> dict:
    """Second link: uses the validated token to look up a user."""
    # In a real app, you'd decode a JWT and query the database
    return {"username": "alice", "token": token}


CurrentUser = Annotated[dict, Depends(get_current_user)]


@app.get("/me")
def me(user: CurrentUser):
    """
    FastAPI resolves the full dependency chain:
    get_token → get_current_user → endpoint
    Results are cached within a single request.
    """
    return user


@app.get("/admin")
def admin(user: CurrentUser):
    """Another endpoint reusing the same dependency chain."""
    return {"message": f"Welcome admin {user['username']}"}
