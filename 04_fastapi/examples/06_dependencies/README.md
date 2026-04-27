# 06 — Dependency Injection

Learn FastAPI's powerful dependency injection system — share logic, improve testability, and manage resources cleanly.

## What You Will Learn

- What dependency injection is and why FastAPI's DI system is powerful
- How to create function, class, and yield-based dependencies
- How to chain dependencies (dependencies that depend on other dependencies)
- How to apply dependencies globally and override them in tests

## Files

| File | What It Teaches |
|------|-----------------|
| `simple_dependency.py` | Function dependencies with `Annotated` + `Depends` |
| `class_dependency.py` | Class-based dependencies with typed attributes |
| `yield_dependency.py` | Yield dependencies for setup/teardown (DB sessions, file handles) |
| `dependency_chain.py` | Chained dependencies and global dependencies |

## How to Run

```bash
# From this directory — pick any file
uvicorn simple_dependency:app --reload
uvicorn class_dependency:app --reload
uvicorn yield_dependency:app --reload
uvicorn dependency_chain:app --reload
```

Then visit http://127.0.0.1:8000/docs to see how dependency parameters appear in the API docs.

## Key Concepts

### Function Dependencies
Any callable can be a dependency. Use `Annotated` for clean type aliases:
```python
def pagination(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

Page = Annotated[dict, Depends(pagination)]

@app.get("/items")
def list_items(page: Page):
    ...
```

### Class Dependencies
Classes give you typed attributes instead of dictionaries:
```python
class Pager:
    def __init__(self, skip: int = 0, limit: int = 10):
        self.skip = skip
        self.limit = limit
```

### Yield Dependencies (Setup / Teardown)
Use `yield` for resources that need cleanup — perfect for DB sessions:
```python
def get_db():
    db = SessionLocal()
    try:
        yield db       # ← the endpoint uses db here
    finally:
        db.close()     # ← cleanup runs after the request
```

### Why This Matters
- **Share logic** — reuse pagination, auth, filters across endpoints
- **Testability** — swap real deps for fakes with `app.dependency_overrides`
- **Auto-documented** — dep parameters appear in Swagger UI

See `docs/06_dependencies.md` for the full theory.
