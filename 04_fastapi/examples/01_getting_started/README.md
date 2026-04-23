# 01 — Getting Started

Your very first FastAPI application. One file, one endpoint, instant interactive docs.

## What You Will Learn

- How to create a minimal API with a single endpoint
- How to run the development server with hot-reload
- How the automatic interactive docs work (`/docs`, `/redoc`)
- How type hints drive automatic validation

## Files

| File | What It Teaches |
|------|-----------------|
| `main.py` | Hello World app with root endpoint and a path parameter |

## How to Run

```bash
# From this directory
uvicorn main:app --reload

# Or from the repo root
uvicorn examples.01_getting_started.main:app --reload
```

Then visit:

| URL | What You See |
|-----|-------------|
| http://127.0.0.1:8000/ | Hello World JSON response |
| http://127.0.0.1:8000/items/42 | Path parameter example |
| http://127.0.0.1:8000/docs | Swagger UI — interactive API explorer |
| http://127.0.0.1:8000/redoc | ReDoc — polished reference docs |

## Key Concepts

### Creating the App
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello, World!"}
```

- `FastAPI()` creates the application instance
- `@app.get("/")` registers a GET route at `/`
- The return value (dict) is automatically converted to JSON

### Running the Server
- `uvicorn main:app` means: file `main.py`, variable `app`
- `--reload` watches for file changes and restarts automatically

### Automatic Docs
FastAPI generates an OpenAPI schema from your code and serves two UIs:
- `/docs` → **Swagger UI** — try endpoints live in the browser
- `/redoc` → **ReDoc** — clean reference documentation
- `/openapi.json` → raw JSON schema

See `docs/01_getting_started.md` for the full theory.
