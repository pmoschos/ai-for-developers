# 02 — Path & Query Parameters

Learn how FastAPI extracts data from the URL — both from the path (`/users/42`) and from query strings (`?skip=0&limit=10`).

## What You Will Learn

- How to declare path parameters with `{name}` syntax
- How type hints drive automatic validation and conversion
- How to constrain values with `Enum`, `Path(...)`, and `Query(...)`
- The difference between path parameters and query parameters
- How to handle optional values, defaults, lists, and booleans

## Files

| File | What It Teaches |
|------|-----------------|
| `path_params.py` | Basic path parameters with type hints |
| `enum_params.py` | Restricting path values to a fixed set with `Enum` |
| `path_validation.py` | Numeric constraints with `Path(ge=1, le=10000)` |
| `query_params.py` | Query parameters with defaults, optional values, validation |
| `query_lists.py` | List and boolean query parameters |

## How to Run

```bash
# From this directory — pick any file
uvicorn path_params:app --reload
uvicorn enum_params:app --reload
uvicorn path_validation:app --reload
uvicorn query_params:app --reload
uvicorn query_lists:app --reload
```

Then visit http://127.0.0.1:8000/docs to try each endpoint interactively.

## Key Concepts

### Path Parameters
Anything inside `{curly_braces}` in the route becomes a path parameter:
```python
@app.get("/users/{user_id}")
def get_user(user_id: int):   # type hint → auto validation
    ...
```
- `GET /users/42` → `{"user_id": 42}` ✅
- `GET /users/abc` → `422 Unprocessable Entity` ❌

### Query Parameters
Any function argument **not** in the path is a query parameter. Defaults make them optional:
```python
@app.get("/items")
def list_items(skip: int = 0, limit: int = 10):
    ...
# /items?skip=20&limit=5
```

### Validation with Path() and Query()
```python
item_id: Annotated[int, Path(ge=1, le=10_000)]
q: Annotated[str | None, Query(min_length=3, max_length=50)] = None
```

See `docs/02_parameters.md` for the full theory.
