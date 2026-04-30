"""
Users Router — Registration and user endpoints.

POST /users/register → create a new user
GET  /users/me       → current user info (auth required)
GET  /users/admin    → admin-only endpoint
"""

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.dependencies import CurrentUser, SessionDep
from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from app.security import hash_password

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, session: SessionDep):
    """
    Register a new user.
    Username 'admin' automatically gets admin privileges (for demo purposes).
    """
    existing = session.exec(
        select(User).where(User.username == data.username)
    ).first()
    if existing:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )
    user = User(
        username=data.username,
        hashed_password=hash_password(data.password),
        is_admin=(data.username == "admin"),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/me", response_model=UserOut)
def me(user: CurrentUser):
    """Return the current authenticated user's info."""
    return user


@router.get("/admin")
def admin_only(user: CurrentUser):
    """Admin-only endpoint. Returns 403 for non-admin users."""
    if not user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admins only")
    return {"secret": "42", "message": f"Welcome, admin {user.username}!"}
