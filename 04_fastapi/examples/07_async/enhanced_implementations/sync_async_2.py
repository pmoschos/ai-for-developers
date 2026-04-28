"""
07 — Async: Sync vs Async Endpoints

This example demonstrates the practical difference between synchronous
and asynchronous FastAPI route handlers.

Covered concepts:
1. Sync endpoints (`def`)
   FastAPI runs them in a threadpool, so blocking synchronous code does not
   block the main event loop.

2. Async endpoints (`async def`)
   FastAPI runs them on the event loop. They are ideal when you need to await
   asynchronous I/O libraries.

3. Blocking vs non-blocking operations
   - blocking calls are acceptable inside sync endpoints
   - non-blocking awaited calls should be used inside async endpoints

4. Choosing the right style
   Use `def` for synchronous libraries or CPU-bound logic.
   Use `async def` when working with async-compatible I/O libraries.

Run:
    uvicorn examples.07_async.sync_vs_async:app --reload

Alternative:
    fastapi dev sync_vs_async.py

Open API docs:
    http://localhost:8000/docs

Try:
    GET /sync
        -> runs in a threadpool

    GET /async
        -> runs on the event loop
"""

import asyncio
import time

from fastapi import FastAPI

# Create the FastAPI application instance.
# Its metadata appears in the generated Swagger/OpenAPI docs.
app = FastAPI(
    title="Sync vs Async",
    description=(
        "Demonstrates the behavioral difference between synchronous and "
        "asynchronous FastAPI endpoints."
    ),
    version="1.0.0",
)


@app.get(
    "/sync",
    summary="Run a synchronous endpoint",
    description=(
        "Demonstrates a standard `def` endpoint. FastAPI runs it in a "
        "threadpool, which makes it suitable for synchronous/blocking code."
    ),
    tags=["Async"],
)
def sync_endpoint():
    """
    Run a synchronous route handler.

    Because this endpoint is declared with plain `def`, FastAPI executes it
    in a threadpool instead of directly on the event loop.

    That means blocking operations such as:
    - `time.sleep(...)`
    - traditional database drivers
    - blocking HTTP libraries
    are acceptable here from the event loop's perspective.

    Important note:
    This does not make blocking work magically efficient.
    It only prevents that work from blocking the async event loop directly.

    This style is appropriate when:
    - you use synchronous libraries,
    - you have existing blocking code,
    - you do CPU-oriented work that is not awaitable.
    """
    time.sleep(1)  # simulates synchronous blocking work
    return {
        "style": "sync",
        "note": "Ran in threadpool",
    }


@app.get(
    "/async",
    summary="Run an asynchronous endpoint",
    description=(
        "Demonstrates an `async def` endpoint. It runs on the event loop and "
        "should use awaited non-blocking operations."
    ),
    tags=["Async"],
)
async def async_endpoint():
    """
    Run an asynchronous route handler.

    Because this endpoint is declared with `async def`, FastAPI runs it
    directly on the event loop.

    Inside async endpoints, you should use non-blocking awaitable operations,
    such as:
    - async HTTP clients
    - async database drivers
    - async Redis clients
    - `await asyncio.sleep(...)`

    Important rule:
    Do not use blocking calls such as `time.sleep(...)` or blocking network
    requests directly inside `async def`, because they block the event loop
    and reduce concurrency for the whole application.

    This style is appropriate when:
    - your libraries are async-compatible,
    - the endpoint performs I/O-bound work,
    - you want efficient concurrency with `await`.
    """
    await asyncio.sleep(1)  # non-blocking simulated async work
    return {
        "style": "async",
        "note": "Ran on event loop",
    }