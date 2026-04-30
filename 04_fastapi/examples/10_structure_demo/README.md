# 10 — Project Structure

Learn how to grow a single-file app into a well-organized multi-file project using `APIRouter`, typed settings, and proper separation of concerns.

## What You Will Learn

- How to split routes by feature using `APIRouter`
- How to manage settings from environment variables with `pydantic-settings`
- A practical project layout for medium-sized APIs
- How to wire everything together in `main.py`

## Where Is the Code?

This section does not contain standalone example files. Instead, look at the **`app/` directory at the repository root** — it **is** the example.

```
app/
├── __init__.py
├── main.py           # FastAPI() + lifespan + routers + CORS + middleware
├── config.py         # Typed settings from .env (pydantic-settings)
├── db.py             # Engine + get_session dependency
├── security.py       # Password hashing + JWT helpers
├── dependencies.py   # get_current_user, pagination
├── exceptions.py     # Custom exception class + handler
├── models/           # SQLModel tables (Hero, User)
├── schemas/          # Pydantic request/response models
└── routers/          # One APIRouter per feature (auth, heroes, users)
```

## How to Run

```bash
# From the repo root
uvicorn app.main:app --reload
```

Then visit http://127.0.0.1:8000/docs to explore all endpoints.

## Key Concepts

### APIRouter — Split by Feature
Each feature gets its own router file. Wire them in `main.py`:
```python
# routers/heroes.py
router = APIRouter(prefix="/heroes", tags=["heroes"])

@router.get("")
def list_heroes(...):
    ...

# main.py
app.include_router(heroes.router)
```

### Typed Settings
Use `pydantic-settings` for environment variables with types, validation, and defaults:
```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    database_url: str = "sqlite:///./database.db"
    secret_key: str
```

### Key Takeaways

1. **APIRouter** — each router file is a "mini FastAPI" with its own prefix and tags
2. **Settings** — `pydantic-settings` reads from `.env` with typed defaults
3. **Separation** — models (DB tables), schemas (API contracts), routers (endpoints)

See `docs/10_project_structure.md` for the full theory.
