# 05 — Error Handling

Learn how to return proper HTTP errors, create custom exception handlers, and reshape validation error responses.

## What You Will Learn

- How to raise `HTTPException` for standard HTTP errors (404, 400, 401, etc.)
- How to create custom exception classes and register handlers
- How to override the default Pydantic validation error response (422 → 400)

## Files

| File | What It Teaches |
|------|-----------------|
| `http_exception.py` | Basic `HTTPException` usage for 404 and other errors |
| `custom_handler.py` | Custom exception class + registered handler |
| `validation_override.py` | Overriding the default 422 validation error format |

## How to Run

```bash
# From this directory — pick any file
uvicorn http_exception:app --reload
uvicorn custom_handler:app --reload
uvicorn validation_override:app --reload
```

Then visit http://127.0.0.1:8000/docs and try triggering errors (e.g., request a nonexistent item).

## Key Concepts

### HTTPException
Raise it anywhere in your code to return an HTTP error:
```python
from fastapi import HTTPException, status

raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Item not found",
)
```

### Custom Exception Handlers
1. Define a Python exception class
2. Register a handler with `@app.exception_handler(YourException)`
3. Return a `JSONResponse` with your custom error shape

```python
class ItemNotFoundError(Exception):
    def __init__(self, item_id: int):
        self.item_id = item_id

@app.exception_handler(ItemNotFoundError)
async def handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": f"Item {exc.item_id} not found"},
    )
```

### Overriding Validation Errors
```python
@app.exception_handler(RequestValidationError)
async def validation_handler(request, exc):
    return JSONResponse(status_code=400, content={...})
```

See `docs/05_errors.md` for the full theory.
