from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict

app = FastAPI(
    title="Dependency Chains - Production Style",
    description=(
        "Example of chained FastAPI dependencies using Header-based token "
        "authentication and Pydantic models."
    ),
    version="1.0.0",
)


# -----------------------------
# Pydantic models
# -----------------------------
class TokenData(BaseModel):
    """
    Internal model representing validated token information.

    In a real application this might contain:
    - subject/user id
    - scopes
    - expiration
    - tenant id
    """
    token: str
    subject: str


class User(BaseModel):
    """
    Public user model returned by the API.
    """
    model_config = ConfigDict(from_attributes=True)

    username: str
    full_name: str | None = None
    is_admin: bool = False


class AdminMessage(BaseModel):
    """
    Response model for admin endpoint.
    """
    message: str
    user: User


# -----------------------------
# Fake persistence/auth layer
# -----------------------------
FAKE_TOKENS_DB = {
    "secret": {
        "subject": "alice",
    },
    "admin-secret": {
        "subject": "admin",
    },
}

FAKE_USERS_DB = {
    "alice": {
        "username": "alice",
        "full_name": "Alice Johnson",
        "is_admin": False,
    },
    "admin": {
        "username": "admin",
        "full_name": "System Administrator",
        "is_admin": True,
    },
}


# -----------------------------
# Dependencies
# -----------------------------
def get_token_data(
    x_token: Annotated[
        str,
        Header(
            alias="X-Token",
            description="Authentication token sent in the X-Token header",
            examples=["secret", "admin-secret"],
        ),
    ]
) -> TokenData:
    """
    Extract and validate the authentication token from request headers.

    Notes:
    - `alias="X-Token"` ensures the public HTTP header name is exactly X-Token.
    - Missing header usually leads to 422 validation error from FastAPI.
    - Invalid token leads to 401 Unauthorized.
    """
    token_payload = FAKE_TOKENS_DB.get(x_token)

    if token_payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    return TokenData(
        token=x_token,
        subject=token_payload["subject"],
    )


def get_current_user(
    token_data: Annotated[TokenData, Depends(get_token_data)]
) -> User:
    """
    Resolve the current user from validated token data.

    This dependency depends on `get_token_data`, so FastAPI executes:
        get_token_data -> get_current_user -> endpoint

    In a real app this could:
    - decode JWT claims
    - load user from database
    - verify account status
    - attach roles/permissions
    """
    user_data = FAKE_USERS_DB.get(token_data.subject)

    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found for this token",
        )

    return User(**user_data)


def get_admin_user(
    user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Authorization dependency for admin-only endpoints.
    """
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    return user


# Reusable aliases for cleaner endpoint signatures
CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(get_admin_user)]


# -----------------------------
# Routes
# -----------------------------
@app.get(
    "/me",
    response_model=User,
    summary="Return the current authenticated user",
    description=(
        "Validates the X-Token header, resolves the current user, "
        "and returns the authenticated user's public profile."
    ),
    tags=["Auth"],
)
def read_me(user: CurrentUser) -> User:
    """
    Return the authenticated user.

    Dependency chain:
        get_token_data -> get_current_user -> endpoint
    """
    return user


@app.get(
    "/admin",
    response_model=AdminMessage,
    summary="Admin endpoint",
    description=(
        "Requires a valid X-Token header and admin privileges."
    ),
    tags=["Auth"],
)
def read_admin(user: AdminUser) -> AdminMessage:
    """
    Return an admin-only response.

    Dependency chain:
        get_token_data -> get_current_user -> get_admin_user -> endpoint
    """
    return AdminMessage(
        message=f"Welcome admin {user.username}",
        user=user,
    )