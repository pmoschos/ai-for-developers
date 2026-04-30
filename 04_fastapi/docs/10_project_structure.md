# 10 — Project Structure

<p align="center">
  <img src="images/project_structure_layout.png" alt="Project Structure Layout" width="720" style="max-width: 100%; border-radius: 8px;" />
</p>

## What You Will Learn

- How to grow a single-file app into a multi-file project
- How to use `APIRouter` to split routes by feature
- How to manage settings from environment variables with `pydantic-settings`
- A practical project layout for medium-sized APIs

---

## When to Split

A single `main.py` works fine for small apps and learning. But as your app grows, you'll hit problems:

| Symptom | Solution |
|---------|----------|
| `main.py` is 500+ lines | Split routes into separate files |
| Hardcoded secrets in source code | Use environment variables |
| Duplicated DB setup code | Extract into a shared module |
| Hard to find where a route is defined | Organize by feature |

---

## APIRouter — Split Routes by Feature

`APIRouter` is a "mini FastAPI" — it has the same interface (`@router.get`, `@router.post`, etc.) but is designed to be wired into the main app:

### Step 1: Create a Router

```python
# routers/heroes.py
from fastapi import APIRouter

router = APIRouter(
    prefix="/heroes",      # all routes start with /heroes
    tags=["Heroes"],       # grouped in Swagger UI
)

@router.get("")
def list_heroes():
    ...

@router.post("", status_code=201)
def create_hero(hero: HeroCreate):
    ...

@router.get("/{hero_id}")
def get_hero(hero_id: int):
    ...
```

### Step 2: Wire It in main.py

```python
# main.py
from fastapi import FastAPI
from app.routers import heroes, users, auth

app = FastAPI()

app.include_router(heroes.router)
app.include_router(users.router)
app.include_router(auth.router)
```

### What This Gives You:

- `/heroes` → handled by `routers/heroes.py`
- `/users` → handled by `routers/users.py`
- `/auth` → handled by `routers/auth.py`
- Swagger UI groups endpoints by tags automatically

---

## Recommended Project Layout

```
myapi/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI() + lifespan + routers + middleware
│   ├── config.py            # Settings from .env (pydantic-settings)
│   ├── db.py                # Engine + get_session dependency
│   ├── security.py          # Password hashing + JWT helpers
│   ├── dependencies.py      # Shared dependencies (auth, pagination)
│   ├── exceptions.py        # Custom exceptions + handlers
│   │
│   ├── models/              # SQLModel table definitions
│   │   ├── __init__.py
│   │   ├── hero.py
│   │   └── user.py
│   │
│   ├── schemas/             # Pydantic request/response models
│   │   ├── __init__.py
│   │   ├── hero.py
│   │   └── user.py
│   │
│   └── routers/             # One APIRouter per feature
│       ├── __init__.py
│       ├── auth.py
│       ├── heroes.py
│       └── users.py
│
├── tests/                   # Test files
│   ├── conftest.py
│   ├── test_heroes.py
│   └── test_auth.py
│
├── .env                     # Environment variables (never commit!)
├── .env.example             # Template for .env
├── requirements.txt         # Dependencies
└── README.md
```

### Why This Structure?

| Directory | Responsibility | Changes When... |
|-----------|---------------|-----------------|
| `models/` | Database tables | Schema evolves |
| `schemas/` | API contracts | Request/response formats change |
| `routers/` | HTTP endpoints | New features added |
| `config.py` | Settings | Deployment environment changes |
| `db.py` | DB connection | Database technology changes |
| `security.py` | Auth helpers | Auth strategy changes |

### Models vs Schemas

This is a common point of confusion:

| | Models (`models/`) | Schemas (`schemas/`) |
|---|---|---|
| **Inherits from** | `SQLModel` with `table=True` | `SQLModel` or `BaseModel` |
| **Maps to** | Database table | JSON request/response |
| **Has** | `id`, `primary_key`, `foreign_key` | Only client-facing fields |
| **Example** | `User` with `hashed_password` | `UserRead` without password |

---

## Typed Settings with pydantic-settings

Use `pydantic-settings` to load configuration from environment variables with **types, validation, and defaults**:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",       # read from .env file
        extra="ignore",        # ignore extra env vars
    )

    # These are read from environment variables
    database_url: str = "sqlite:///./database.db"
    secret_key: str           # REQUIRED — no default, must be set
    access_token_expire_minutes: int = 30
    cors_origins: list[str] = ["http://localhost:3000"]
    debug: bool = True
```

### Priority Order (highest first):

1. **Environment variable** — `export SECRET_KEY=abc123`
2. **`.env` file** — `SECRET_KEY=abc123`
3. **Default value** — `secret_key: str = "fallback"`

### Singleton Pattern with `@lru_cache`

```python
from functools import lru_cache

@lru_cache
def get_settings() -> Settings:
    return Settings()

# Always call get_settings() — it returns the same cached instance
settings = get_settings()
```

### `.env` File Example

```ini
SECRET_KEY=your-production-secret-here
DATABASE_URL=postgresql://user:pass@localhost/mydb
DEBUG=false
CORS_ORIGINS=["https://myapp.com"]
```

> **Never commit `.env` to version control.** Add it to `.gitignore`.
> Provide a `.env.example` template instead.

---

## Wiring It All Together in main.py

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db import create_db_and_tables
from app.routers import auth, heroes, users

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="My API", lifespan=lifespan)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(heroes.router)
app.include_router(users.router)
```

---

## Code Examples

→ See the `app/` directory at the repository root — it **is** the working example.

→ See `examples/10_structure_demo/README.md` for a guided walkthrough.
