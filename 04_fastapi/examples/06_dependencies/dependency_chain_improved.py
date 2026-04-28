"""
06 — Dependencies: Dependency Chains & Role-Based Access (Improved)

Builds on dependency_chain.py by adding:
  - A fake user database with multiple users and roles
  - A 3-level dependency chain: token → user → role check
  - A parameterised dependency (require_role) that creates
    different dependencies based on the role you pass in

Run:  uvicorn examples.06_dependencies.dependency_chain_improved:app --reload

Try (use the X-Token header in /docs → click "Try it out"):

  GET /me
    X-Token: token-alice   → 200  (alice, role: admin)
    X-Token: token-bob     → 200  (bob,   role: viewer)
    X-Token: wrong         → 401  Invalid token

  GET /admin/dashboard
    X-Token: token-alice   → 200  (alice is admin ✅)
    X-Token: token-bob     → 403  (bob is viewer ❌)

  GET /reports
    X-Token: token-alice   → 200  (admin can view)
    X-Token: token-bob     → 200  (viewer can view)
    without header         → 422  (header required)
"""

from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Dependency Chains (Improved)")


# Fake user database

USERS_DB = {
    "token-alice": {"username": "alice", "role": "admin"},
    "token-bob":   {"username": "bob",   "role": "viewer"},
    "token-carol": {"username": "carol", "role": "editor"},
}


# Dependency 1: Validate the token

def get_token(x_token: Annotated[str, Header()]) -> str:
    """
    First link in the chain: check that the X-Token header exists
    and corresponds to a known user.
    """
    if x_token not in USERS_DB:
        raise HTTPException(status_code=401, detail="Invalid token")
    return x_token


# Dependency 2: Look up the user

def get_current_user(token: Annotated[str, Depends(get_token)]) -> dict:
    """
    Second link: takes the validated token (from Dep 1) and returns
    the full user record from the fake database.

    The chain so far:
        get_token → get_current_user
    """
    user = USERS_DB[token]
    return {"username": user["username"], "role": user["role"], "token": token}


# Type alias so endpoints just write `user: CurrentUser`
CurrentUser = Annotated[dict, Depends(get_current_user)]


# Dependency 3: Role-based access (parameterised)

def require_role(*allowed_roles: str):
    """
    A dependency FACTORY — it returns a new dependency function
    that checks whether the current user has one of the allowed roles.

    Usage:
        Depends(require_role("admin"))
        Depends(require_role("admin", "editor"))

    This is a 3-level chain:
        get_token → get_current_user → role check
    """
    def role_checker(user: CurrentUser) -> dict:
        if user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Role '{user['role']}' not allowed. "
                       f"Required: {', '.join(allowed_roles)}",
            )
        return user
    return role_checker


# Endpoints

@app.get("/me")
def me(user: CurrentUser):
    """
    Any authenticated user can access this.
    Chain: get_token → get_current_user → endpoint

    Try:
        X-Token: token-alice  → alice (admin)
        X-Token: token-bob    → bob   (viewer)
    """
    return user


@app.get("/admin/dashboard")
def admin_dashboard(
    user: Annotated[dict, Depends(require_role("admin"))],
):
    """
    Only admins can access this.
    Chain: get_token → get_current_user → require_role("admin") → endpoint

    Try:
        X-Token: token-alice  → 200 ✅
        X-Token: token-bob    → 403 ❌
    """
    return {"message": f"Welcome to the admin panel, {user['username']}!"}


@app.get("/reports")
def view_reports(
    user: Annotated[dict, Depends(require_role("admin", "viewer", "editor"))],
):
    """
    Admins, viewers, and editors can all access this.

    Try:
        X-Token: token-alice  → 200 ✅ (admin)
        X-Token: token-bob    → 200 ✅ (viewer)
        X-Token: token-carol  → 200 ✅ (editor)
    """
    return {
        "message": f"Here are your reports, {user['username']}",
        "role": user["role"],
    }


class PublishRequest(BaseModel):
    """The body payload for publishing content."""
    content: str
    title: str = "Untitled"


@app.post("/editor/publish")
def publish(
    body: PublishRequest,
    user: Annotated[dict, Depends(require_role("admin", "editor"))],
):
    """
    Only admins and editors can publish.
    Requires a JSON body with `text` (required) and `title` (optional).

    Try:
        X-Token: token-alice  → 200 ✅ (admin)
        X-Token: token-carol  → 200 ✅ (editor)
        X-Token: token-bob    → 403 ❌ (viewer)
    """
    return {
        "message": f"{user['username'].capitalize()} published successfully",
        "title": body.title,
        "content": body.content,
    }
