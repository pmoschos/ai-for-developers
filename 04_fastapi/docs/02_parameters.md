# 02 — Path & Query Parameters

<p align="center">
  <img src="images/url_parameters_diagram.png" alt="URL Parameters Diagram" width="720" style="max-width: 100%; border-radius: 8px;" />
</p>

## What You Will Learn

- How to declare path parameters with `{name}` syntax
- How type hints drive automatic validation and conversion
- How to constrain values with `Enum`, `Path(...)`, and `Query(...)`
- The difference between path parameters and query parameters
- How to handle optional values, defaults, lists, and booleans in queries

---

## Path Parameters

Anything inside `{curly_braces}` in the route becomes a **path parameter**. FastAPI binds it to the matching function argument by name.

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}
```

### What the type hint does:

| Request | Type Hint | Result |
|---------|-----------|--------|
| `GET /users/42` | `int` | `{"user_id": 42}` ✅ auto-converted to int |
| `GET /users/abc` | `int` | `422 Unprocessable Entity` ❌ validation error |
| `GET /users/3.14` | `int` | `422 Unprocessable Entity` ❌ not an integer |

> **Key insight:** The type hint is not just documentation — it's a runtime contract.
> FastAPI validates and converts the value automatically.

### Route Order Matters

Fixed routes must come **before** parameterized routes:

```python
@app.get("/users/me")         # ← this MUST be first
def get_current_user(): ...

@app.get("/users/{user_id}")   # ← otherwise "me" would match as user_id
def get_user(user_id: int): ...
```

---

## Enum Constraints

Use Python's `Enum` to restrict a path parameter to a fixed set of values:

```python
from enum import Enum

class Role(str, Enum):
    admin = "admin"
    editor = "editor"
    viewer = "viewer"

@app.get("/roles/{role}")
def get_role(role: Role):
    return {"role": role.value}
```

- `GET /roles/admin` → `{"role": "admin"}` ✅
- `GET /roles/hacker` → `422` ❌ not a valid enum value
- Swagger UI shows a **dropdown** with the valid choices

---

## Path Validation

Use `Path(...)` from FastAPI for numeric constraints and metadata:

```python
from typing import Annotated
from fastapi import Path

@app.get("/items/{item_id}")
def get_item(
    item_id: Annotated[int, Path(ge=1, le=10_000, description="Item ID")]
):
    ...
```

| Constraint | Meaning |
|-----------|---------|
| `ge=1` | Greater than or equal to 1 |
| `le=10_000` | Less than or equal to 10,000 |
| `gt=0` | Strictly greater than 0 |
| `lt=100` | Strictly less than 100 |
| `description=` | Shows in Swagger UI docs |
| `title=` | Schema title in OpenAPI |

---

## Query Parameters

Any function argument that is **not** in the URL path is automatically treated as a **query parameter**:

```python
@app.get("/items")
def list_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

# Client calls: GET /items?skip=20&limit=5
```

### Path vs Query — How FastAPI Decides

```python
@app.get("/users/{user_id}/posts")
def get_posts(user_id: int, skip: int = 0, limit: int = 10):
    ...
#               ^^^^^^^^ path param       ^^^^^^^^^^^^^ query params
#               (in the URL path)         (not in the URL path)
```

### Optional Query Parameters

Use `None` as the default to make a query parameter optional:

```python
@app.get("/search")
def search(q: str | None = None):
    if q:
        return {"results": f"searching for {q}"}
    return {"results": "no query provided"}
```

---

## Query Validation

Use `Query(...)` for string constraints and documentation:

```python
from typing import Annotated
from fastapi import Query

@app.get("/search")
def search(
    q: Annotated[str | None, Query(
        min_length=3,
        max_length=50,
        description="Search query string",
    )] = None,
):
    ...
```

| Constraint | Applies To | Meaning |
|-----------|-----------|---------|
| `min_length=3` | strings | At least 3 characters |
| `max_length=50` | strings | At most 50 characters |
| `pattern=r"^[a-z]+$"` | strings | Must match the regex |
| `ge=0` | numbers | Greater or equal to 0 |
| `le=100` | numbers | Less or equal to 100 |

---

## Lists and Booleans in Queries

### List Parameters
Repeat a query key to pass multiple values:

```python
@app.get("/filter")
def filter_items(tags: list[str] = Query(default=[])):
    return {"tags": tags}

# GET /filter?tags=red&tags=blue → {"tags": ["red", "blue"]}
```

### Boolean Parameters
FastAPI accepts multiple truthy/falsy values:

| Truthy | Falsy |
|--------|-------|
| `true`, `True`, `1`, `yes`, `on` | `false`, `False`, `0`, `no`, `off` |

```python
@app.get("/items")
def list_items(in_stock: bool = True):
    ...
# GET /items?in_stock=false
```

---

## Code Examples

→ See `examples/02_parameters/`

| File | Concept |
|------|---------|
| `path_params.py` | Basic path parameters |
| `enum_params.py` | Enum-constrained values |
| `path_validation.py` | `Path(...)` constraints |
| `query_params.py` | Query parameters with defaults |
| `query_lists.py` | List and boolean query params |
