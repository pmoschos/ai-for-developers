"""
07 — Async: Sync vs Async Endpoints

Run:  uvicorn examples.07_async.sync_vs_async:app --reload

Try:
  GET /sync  → runs in a threadpool
  GET /async → runs on the event loop
"""

import asyncio
import time

from fastapi import FastAPI

app = FastAPI(title="Sync vs Async")


@app.get("/sync")
def sync_endpoint():
    """
    Plain `def` — FastAPI runs this in a threadpool.
    It never blocks the event loop.
    Fine for CPU work or synchronous libraries.
    """
    time.sleep(0.1)  # simulates sync work — OK in def
    return {"style": "sync", "note": "Ran in threadpool"}


@app.get("/async")
async def async_endpoint():
    """
    `async def` — runs directly on the event loop.
    Use when you `await` async libraries (httpx, asyncpg, redis).
    NEVER use blocking calls (time.sleep, requests.get) here!
    """
    await asyncio.sleep(0.1)  # non-blocking sleep — correct in async def
    return {"style": "async", "note": "Ran on event loop"}
