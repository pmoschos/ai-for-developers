# 04 — Responses & Status Codes

Learn how to control what your API sends back — filtering fields, setting status codes, and returning different content types.

## What You Will Learn

- How to use `response_model` to filter outgoing data (e.g., hide passwords)
- How to set custom HTTP status codes (201 Created, 204 No Content, etc.)
- How to return HTML, plain text, redirects, and file downloads

## Files

| File | What It Teaches |
|------|-----------------|
| `response_model.py` | Using `response_model` to filter sensitive fields from responses |
| `status_codes.py` | Setting custom HTTP status codes on endpoints |
| `custom_responses.py` | Returning HTML, plain text, and redirect responses |

## How to Run

```bash
# From this directory — pick any file
uvicorn response_model:app --reload
uvicorn status_codes:app --reload
uvicorn custom_responses:app --reload
```

Then visit http://127.0.0.1:8000/docs to try each endpoint.

## Key Concepts

### Response Models — Filtering Output
```python
@app.post("/users", response_model=UserOut)
def create_user(user: UserIn):
    return user   # password is filtered out automatically
```
`response_model` strips any fields not in the output model — a safety net for keeping secrets out of responses.

### Status Codes
```python
from fastapi import status

@app.post("/items", status_code=status.HTTP_201_CREATED)
def create_item(item: Item):
    ...

@app.delete("/items/{id}", status_code=204)
def delete_item(id: int):
    ...
```

### Custom Response Types
| Class | Use Case |
|-------|----------|
| `JSONResponse` | Default — JSON output |
| `HTMLResponse` | Return raw HTML |
| `PlainTextResponse` | Plain text |
| `RedirectResponse` | HTTP redirect |
| `FileResponse` | Serve a file from disk |
| `StreamingResponse` | Stream large data |

See `docs/04_responses.md` for the full theory.
