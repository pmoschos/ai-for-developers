# 07 — Async & Concurrency

Learn the difference between `def` and `async def` in FastAPI, and how to run background work after sending a response.

## What You Will Learn

- The difference between sync (`def`) and async (`async def`) endpoints
- When to use each one — and what happens under the hood
- How to run fire-and-forget tasks with `BackgroundTasks`

## Files

| File | What It Teaches |
|------|-----------------|
| `sync_vs_async.py` | Side-by-side comparison of `def` vs `async def` endpoints |
| `background_tasks.py` | Running work after the response with `BackgroundTasks` |

## How to Run

```bash
# From this directory — pick any file
uvicorn sync_vs_async:app --reload
uvicorn background_tasks:app --reload
```

Then visit http://127.0.0.1:8000/docs to try the endpoints.

For `background_tasks.py`, check the terminal and `background_log.txt` after calling the endpoint.

## Key Concepts

### `def` vs `async def`
Both work in FastAPI. The framework handles them differently:

| | `def` (sync) | `async def` (async) |
|---|---|---|
| **Runs on** | Thread pool | Event loop |
| **Good for** | CPU work, sync libraries | `await`-ing async I/O |
| **Blocks event loop?** | No (runs in thread) | Only if you forget `await` |

### When to Use Async

| Avoid in `async def` | Use instead |
|---|---|
| `requests.get(url)` | `httpx.AsyncClient` |
| `time.sleep(3)` | `asyncio.sleep(3)` |
| `psycopg2.connect()` | `asyncpg` |

**Rule of thumb:** `async def` if you're awaiting I/O; `def` for sync libraries.

### Background Tasks
Run work **after** the response is sent. Great for logging, emails, or lightweight jobs:
```python
@app.post("/send-email")
def send_email(to: str, bg: BackgroundTasks):
    bg.add_task(write_log, f"emailed {to}")
    return {"status": "queued"}
```

For heavy workloads, use a task queue (Celery, RQ, Dramatiq).

See `docs/07_async.md` for the full theory.
