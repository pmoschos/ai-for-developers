# 08 — Database with SQLModel

Learn how to connect FastAPI to a database using SQLModel — which combines Pydantic validation with SQLAlchemy ORM in a single class.

## What You Will Learn

- What SQLModel is and how it unifies Pydantic + SQLAlchemy
- How to define table models with `SQLModel` and `table=True`
- How to set up an engine, session, and dependency injection
- How to implement full CRUD (Create, Read, Update, Delete)
- How to define one-to-many relationships (Team → Heroes)

## Files

| File | What It Teaches |
|------|-----------------|
| `models.py` | Hero + Team SQLModel definitions with relationships |
| `db.py` | Engine setup, session dependency (`SessionDep`), `create_all` |
| `main.py` | Full CRUD app with lifespan startup, all endpoints |

### Enhanced Implementation

The `enhanced_implementations/hero_api/` folder contains a refactored version split into proper modules:

```
enhanced_implementations/hero_api/
├── run.py              # Uvicorn entry point
├── requirements.txt    # fastapi, uvicorn, sqlmodel
└── app/
    ├── main.py         # App + lifespan + router wiring
    ├── db.py           # Engine + session
    ├── models.py       # Hero + Team ORM models
    ├── schemas.py      # Separate request/response schemas
    └── api/
        ├── heroes.py   # Full CRUD + /with-team endpoint
        └── teams.py    # Full CRUD for teams
```

## How to Run

```bash
# Single-file version (from this directory)
uvicorn main:app --reload

# Enhanced multi-file version
cd enhanced_implementations/hero_api
python run.py
```

Then visit http://127.0.0.1:8000/docs to try the CRUD endpoints.

## Key Concepts

### SQLModel = Pydantic + SQLAlchemy
```python
class Hero(SQLModel, table=True):          # table=True → DB table
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    power: str

class HeroCreate(SQLModel):                # no table=True → Pydantic schema
    name: str
    power: str
```

### Session Dependency
```python
def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
```

### CRUD Pattern
- **Create:** `session.add(obj)` → `commit()` → `refresh(obj)`
- **Read:** `session.exec(select(Model).offset(...).limit(...))`
- **Update:** `model_dump(exclude_unset=True)` → `setattr` loop
- **Delete:** `session.delete(obj)` → `commit()`

See `docs/08_database.md` for the full theory.
