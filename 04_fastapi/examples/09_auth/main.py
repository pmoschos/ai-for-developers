"""
09 — Authentication: Full Auth App (Login + Protected Endpoints)

Run:  uvicorn examples.09_auth.main:app --reload
Docs: http://127.0.0.1:8000/docs

Flow:
  1. POST /register → create a user
  2. POST /login → get an access token
  3. Click "Authorize" in Swagger UI, paste the token
  4. GET /me → see your user info
  5. GET /admin → admin-only (register with username "admin")
"""

from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, create_engine, select

# --- Configuration ---

SECRET_KEY = "demo-secret-change-me"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
DATABASE_URL = "sqlite:///./auth_demo.db"

# --- Database Setup ---

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

# --- Models ---


class User(SQLModel, table=True):

    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    is_admin: bool = False


class UserCreate(BaseModel):
    username: str
    password: str

# --- Security Helpers ---

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def hash_password(raw: str) -> str:
    return pwd_context.hash(raw)


def verify_password(raw: str, hashed: str) -> bool:
    return pwd_context.verify(raw, hashed)


def create_access_token(sub: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": sub, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


# --- Dependencies ---


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
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_exception
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]

# --- App ---


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(title="Auth Demo", lifespan=lifespan)


@app.post("/register")
def register(data: UserCreate, session: SessionDep):
    """Register a new user. Username 'admin' gets admin rights."""
    existing = session.exec(select(User).where(User.username == data.username)).first()
    if existing:
        raise HTTPException(400, "Username already taken")
    user = User(
        username=data.username,
        hashed_password=hash_password(data.password),
        is_admin=(data.username == "admin"),
    )
    session.add(user)
    session.commit()
    return {"ok": True, "username": user.username}


@app.post("/login")
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
):
    """Validate credentials and return an access token."""
    user = session.exec(select(User).where(User.username == form.username)).first()
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
def admin_only(user: CurrentUser):
    """Admin-only endpoint. Raises 403 for non-admin users."""
    if not user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admins only")
    return {"secret": "42", "message": f"Welcome, admin {user.username}!"}
