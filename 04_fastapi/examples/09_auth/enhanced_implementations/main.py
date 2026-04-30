import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field as PydanticField
from sqlmodel import Field, Session, SQLModel, create_engine, select

# ============================================================================
# Configuration
# ============================================================================

# Secret used to sign JWT tokens.
# In production, always provide this through environment variables.
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret")

# JWT signing algorithm.
ALGORITHM = "HS256"

# Access token lifetime in minutes.
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# SQLite database URL for local demo purposes.
DATABASE_URL = "sqlite:///./auth_demo.db"

# Create the SQLModel engine.
# check_same_thread=False is required for SQLite when used with FastAPI.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


# ============================================================================
# Database Session Dependency
# ============================================================================

def get_session():
    """
    Yield a database session for a single request.

    FastAPI will call this dependency per request and automatically
    close the session after the request is completed.
    """
    with Session(engine) as session:
        yield session


# Reusable dependency alias for injecting a Session into route handlers.
SessionDep = Annotated[Session, Depends(get_session)]


# ============================================================================
# Database Models and API Schemas
# ============================================================================

class User(SQLModel, table=True):
    """
    Database model representing an application user.

    Attributes:
        id: Primary key.
        username: Unique username used for login.
        hashed_password: Securely hashed password.
        is_admin: Flag indicating whether the user has admin privileges.
    """

    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    is_admin: bool = False


class UserCreate(BaseModel):
    """
    Request body used when registering a new user.

    Validation rules:
        - username: between 3 and 50 characters
        - password: between 8 and 128 characters
    """

    username: str = PydanticField(min_length=3, max_length=50)
    password: str = PydanticField(min_length=8, max_length=128)


class UserRead(BaseModel):
    """
    Public response model for returning user information.

    This excludes sensitive fields such as the hashed password.
    """

    username: str
    is_admin: bool


class Token(BaseModel):
    """
    Response model returned after successful login.

    Attributes:
        access_token: JWT bearer token.
        token_type: Typically 'bearer'.
    """

    access_token: str
    token_type: str


# ============================================================================
# Security Setup
# ============================================================================

# Password hashing context.
# bcrypt is a widely used password hashing scheme.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 bearer token dependency.
# FastAPI uses this in Swagger UI to support the "Authorize" button.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def hash_password(raw: str) -> str:
    """
    Hash a plaintext password.

    Args:
        raw: The plaintext password provided by the user.

    Returns:
        A securely hashed password string.
    """
    return pwd_context.hash(raw)


def verify_password(raw: str, hashed: str) -> bool:
    """
    Verify a plaintext password against its hashed version.

    Args:
        raw: Plaintext password entered during login.
        hashed: Previously stored hashed password from the database.

    Returns:
        True if the password matches, otherwise False.
    """
    return pwd_context.verify(raw, hashed)


def create_access_token(sub: str) -> str:
    """
    Create a signed JWT access token.

    Args:
        sub: Subject of the token, typically the username.

    Returns:
        Encoded JWT token as a string.

    Notes:
        The token contains:
        - sub: identifies the authenticated user
        - iat: issued-at time
        - exp: expiration time
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": sub,
        "iat": now,
        "exp": expire,
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ============================================================================
# Authentication / Authorization Dependencies
# ============================================================================

def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep,
) -> User:
    """
    Decode the bearer token and return the authenticated user.

    Args:
        token: JWT access token extracted from the Authorization header.
        session: Active database session.

    Returns:
        The authenticated User object.

    Raises:
        HTTPException(401): If the token is invalid, expired, malformed,
        or if the referenced user no longer exists.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the JWT and extract the username stored in the "sub" claim.
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if not username:
            raise credentials_exception

    except JWTError:
        # Covers invalid signature, expired token, malformed token, etc.
        raise credentials_exception

    # Look up the user in the database using the username from the token.
    user = session.exec(select(User).where(User.username == username)).first()

    if user is None:
        raise credentials_exception

    return user


# Reusable dependency alias for authenticated routes.
CurrentUser = Annotated[User, Depends(get_current_user)]


def require_admin(user: CurrentUser) -> User:
    """
    Ensure the current authenticated user has admin privileges.

    Args:
        user: Authenticated user resolved by get_current_user.

    Returns:
        The same user object if the user is an admin.

    Raises:
        HTTPException(403): If the authenticated user is not an admin.
    """
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admins only")
    return user


# Reusable dependency alias for admin-only routes.
AdminUser = Annotated[User, Depends(require_admin)]


# ============================================================================
# Application Lifecycle
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup/shutdown lifecycle handler.

    On startup:
        - create database tables if they do not already exist

    On shutdown:
        - no special cleanup is required in this example
    """
    SQLModel.metadata.create_all(engine)
    yield


# Create the FastAPI application instance.
app = FastAPI(title="Auth Demo", lifespan=lifespan)


# ============================================================================
# Routes
# ============================================================================

@app.post("/register", response_model=UserRead, status_code=201)
def register(data: UserCreate, session: SessionDep):
    """
    Register a new user.

    Args:
    - **data**: Incoming user registration payload.
    - **session**: Active database session.

    Returns:
    - A public representation of the newly created user.

    Behavior:
    - Normalizes the username by trimming whitespace and converting to lowercase
    - Rejects duplicate usernames
    - Hashes the password before storing it
    - Grants admin privileges automatically if the username is 'admin'

    Raises:
    - HTTPException(400): If the username is already taken.
    """
    # Normalize username to avoid duplicates such as "Admin" vs "admin".
    username = data.username.strip().lower()

    # Check whether the username already exists.
    existing = session.exec(select(User).where(User.username == username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")

    # Create the new user with a hashed password.
    user = User(
        username=username,
        hashed_password=hash_password(data.password),
        is_admin=(username == "admin"),
    )

    try:
        # Persist the new user in the database.
        session.add(user)
        session.commit()
        session.refresh(user)
    except Exception:
        # Roll back transaction if anything goes wrong.
        session.rollback()
        raise

    return user


@app.post("/login", response_model=Token)
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
):
    """
    Authenticate a user and return a JWT access token.

    Args:
        form: OAuth2 login form containing username and password.
              This is submitted as form data, not JSON.
        session: Active database session.

    Returns:
        A token response containing the access token and token type.

    Raises:
        HTTPException(401): If the username does not exist or the password is incorrect.
    """
    # Normalize username in the same way as during registration.
    username = form.username.strip().lower()

    # Look up the user by username.
    user = session.exec(select(User).where(User.username == username)).first()

    # Reject invalid credentials.
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Return a signed JWT token for authenticated access.
    return {
        "access_token": create_access_token(user.username),
        "token_type": "bearer",
    }


@app.get("/me", response_model=UserRead)
def me(user: CurrentUser):
    """
    Return the currently authenticated user's public profile.

    Args:
        user: Authenticated user injected by dependency.

    Returns:
        Public user information for the current user.
    """
    return user


@app.get("/admin")
def admin_only(user: AdminUser):
    """
    Example admin-only endpoint.

    Args:
        user: Authenticated admin user injected by dependency.

    Returns:
        A simple protected response visible only to admins.
    """
    return {"secret": "42", "message": f"Welcome, admin {user.username}!"}