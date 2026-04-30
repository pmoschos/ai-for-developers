# 11 — Middleware, CORS & Lifespan Events

Learn how to add cross-cutting logic that runs on every request, configure CORS for frontend access, and manage startup/shutdown resources.

## What You Will Learn

- What CORS is and how to configure it in FastAPI
- How to write custom middleware (timing, request IDs, logging)
- How to use lifespan events for startup/shutdown resource management

## Files

| File | What It Teaches |
|------|-----------------|
| `cors_example.py` | CORS middleware configuration for frontend origins |
| `custom_middleware.py` | Custom `TimingMiddleware` with `X-Process-Time` and `X-Request-ID` headers |
| `lifespan_example.py` | Lifespan events: shared httpx client, startup/shutdown, `/joke` endpoint |

## How to Run

```bash
# From this directory — pick any file
uvicorn cors_example:app --reload
uvicorn custom_middleware:app --reload
uvicorn lifespan_example:app --reload
```

Then visit http://127.0.0.1:8000/docs to try each endpoint.

For `lifespan_example.py`, try:
- http://127.0.0.1:8000/ — health check
- http://127.0.0.1:8000/joke — fetches a random joke using the shared httpx client

## Key Concepts

### Request/Response Flow
```
Client Request
   ↓
Middleware (before)
   ↓
Route Handler
   ↓
Middleware (after)
   ↓
Client Response
```

### CORS (Cross-Origin Resource Sharing)
Required when a browser frontend (React, Vue, etc.) calls your API from a different origin:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
> **Warning:** Never ship `allow_origins=["*"]` with `allow_credentials=True`.

### Custom Middleware
Subclass `BaseHTTPMiddleware` to add logic on every request/response:
- Timing headers
- Request IDs for tracing
- Logging

### Lifespan Events
Use `@asynccontextmanager` + `lifespan` to manage shared resources:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP — create clients, DB tables, load models
    app.state.http = httpx.AsyncClient()
    yield
    # SHUTDOWN — close clients, clean up
    await app.state.http.aclose()
```

This replaces the older `@app.on_event("startup")` / `@app.on_event("shutdown")` pattern.

See `docs/11_middleware_and_cors.md` for the full theory.
