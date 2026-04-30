"""
12 — Testing: Part 3 — Testing Authenticated Endpoints

Run:
    pytest examples/12_testing/test_03_auth.py -v

What this file teaches:
    - How to test endpoints that require authentication
    - How to obtain a JWT token during tests and send it in headers
    - How to test registration, login, and protected routes
    - How to test role-based access (admin vs. regular user)
    - How to write reusable auth helper fixtures

Key idea:
    To test protected endpoints, you first register and login
    a test user to get a JWT token, then include it in the
    Authorization header of subsequent requests:

        headers = {"Authorization": f"Bearer {token}"}
        client.get("/protected", headers=headers)
"""

from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Annotated

import pytest
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.testclient import TestClient
from jose import jwt
from passlib.context import CryptContext
from sqlmodel import Field, Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool


# ============================================================================
# App Configuration
# ============================================================================

SECRET_KEY = "test-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# ============================================================================
# Database Layer
# ============================================================================

DATABASE_URL = "sqlite:///./test_auth_demo.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


# ============================================================================
# Models
# ============================================================================

class User(SQLModel, table=True):
    """User table with hashed password and admin flag."""

    __tablename__ = "test_users"

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    is_admin: bool = False


# ============================================================================
# Security
# ============================================================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def hash_password(raw: str) -> str:
    return pwd_context.hash(raw)


def verify_password(raw: str, hashed: str) -> bool:
    return pwd_context.verify(raw, hashed)


def create_access_token(sub: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": sub, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


# ============================================================================
# Dependencies
# ============================================================================

def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep,
) -> User:
    """Decode the JWT, look up the user, or raise 401."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_exception
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_admin(user: CurrentUser) -> User:
    """Ensure the current user is an admin."""
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admins only")
    return user


AdminUser = Annotated[User, Depends(require_admin)]


# ============================================================================
# App and Routes
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(title="Auth Testing Demo", lifespan=lifespan)


@app.post("/register", status_code=201)
def register(data: dict, session: SessionDep):
    """Register a new user. Username 'admin' gets admin rights."""
    username = data["username"].strip().lower()
    password = data["password"]

    existing = session.exec(select(User).where(User.username == username)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Username already taken")

    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password too short")

    user = User(
        username=username,
        hashed_password=hash_password(password),
        is_admin=(username == "admin"),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    return {"username": user.username, "is_admin": user.is_admin}


@app.post("/login")
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
):
    """Validate credentials and return an access token."""
    user = session.exec(
        select(User).where(User.username == form.username.strip().lower())
    ).first()

    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": create_access_token(user.username),
        "token_type": "bearer",
    }


@app.get("/me")
def me(user: CurrentUser):
    """Return the current user's info. Requires authentication."""
    return {"username": user.username, "is_admin": user.is_admin}


@app.get("/admin")
def admin_only(user: AdminUser):
    """Admin-only endpoint."""
    return {"secret": "42", "message": f"Welcome, admin {user.username}!"}


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture(name="session")
def session_fixture():
    """Fresh in-memory database for each test."""
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """TestClient with in-memory DB override."""

    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def register_user(
    client: TestClient,
    username: str = "testuser",
    password: str = "testpass123",
) -> dict:
    """
    Helper: register a user and return the response data.

    Reusable across multiple tests to avoid repeating
    the registration step.
    """
    response = client.post(
        "/register",
        json={"username": username, "password": password},
    )
    return response.json()


def get_auth_headers(
    client: TestClient,
    username: str = "testuser",
    password: str = "testpass123",
) -> dict:
    """
    Helper: register + login a user and return Authorization headers.

    Usage in tests:
        headers = get_auth_headers(client)
        response = client.get("/me", headers=headers)

    This is the most common pattern for testing protected endpoints.
    """
    # Step 1: Register the user.
    register_user(client, username, password)

    # Step 2: Login to get a token.
    # Note: OAuth2PasswordRequestForm expects form data, not JSON.
    response = client.post(
        "/login",
        data={"username": username, "password": password},
    )
    token = response.json()["access_token"]

    # Step 3: Return headers with the Bearer token.
    return {"Authorization": f"Bearer {token}"}


# ============================================================================
# Tests — Registration
# ============================================================================

def test_register_user(client):
    """POST /register creates a new user and returns 201."""
    response = client.post(
        "/register",
        json={"username": "alice", "password": "securepass123"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "alice"
    assert data["is_admin"] is False
    assert "hashed_password" not in data  # never expose password hashes


def test_register_admin(client):
    """Username 'admin' automatically gets admin privileges."""
    response = client.post(
        "/register",
        json={"username": "admin", "password": "adminpass123"},
    )

    assert response.status_code == 201
    assert response.json()["is_admin"] is True


def test_register_duplicate(client):
    """Registering the same username twice returns 409 Conflict."""
    client.post(
        "/register",
        json={"username": "bob", "password": "securepass123"},
    )
    response = client.post(
        "/register",
        json={"username": "bob", "password": "differentpass1"},
    )

    assert response.status_code == 409
    assert "already taken" in response.json()["detail"]


def test_register_short_password(client):
    """Passwords shorter than 8 characters are rejected."""
    response = client.post(
        "/register",
        json={"username": "carol", "password": "short"},
    )

    assert response.status_code == 400


# ============================================================================
# Tests — Login
# ============================================================================

def test_login_success(client):
    """Correct credentials return a JWT access token."""
    register_user(client, "dave", "securepass123")

    response = client.post(
        "/login",
        data={"username": "dave", "password": "securepass123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    """Wrong password returns 401 Unauthorized."""
    register_user(client, "eve", "securepass123")

    response = client.post(
        "/login",
        data={"username": "eve", "password": "wrongpassword"},
    )

    assert response.status_code == 401


def test_login_nonexistent_user(client):
    """Login with an unregistered username returns 401."""
    response = client.post(
        "/login",
        data={"username": "ghost", "password": "anypassword1"},
    )

    assert response.status_code == 401


# ============================================================================
# Tests — Protected Endpoints
# ============================================================================

def test_me_authenticated(client):
    """GET /me with a valid token returns the user's info."""
    headers = get_auth_headers(client)

    response = client.get("/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


def test_me_unauthenticated(client):
    """GET /me without a token returns 401."""
    response = client.get("/me")

    assert response.status_code == 401


def test_me_invalid_token(client):
    """GET /me with a garbage token returns 401."""
    headers = {"Authorization": "Bearer this-is-not-a-real-token"}

    response = client.get("/me", headers=headers)

    assert response.status_code == 401


# ============================================================================
# Tests — Admin Authorization
# ============================================================================

def test_admin_endpoint_as_admin(client):
    """Admin user can access /admin."""
    headers = get_auth_headers(client, username="admin", password="adminpass123")

    response = client.get("/admin", headers=headers)

    assert response.status_code == 200
    assert response.json()["secret"] == "42"
    assert "admin" in response.json()["message"]


def test_admin_endpoint_as_regular_user(client):
    """Non-admin user gets 403 Forbidden on /admin."""
    headers = get_auth_headers(client, username="regularuser", password="userpass1234")

    response = client.get("/admin", headers=headers)

    assert response.status_code == 403
    assert response.json()["detail"] == "Admins only"


def test_admin_endpoint_unauthenticated(client):
    """Unauthenticated request to /admin returns 401, not 403."""
    response = client.get("/admin")

    assert response.status_code == 401
