"""
07 — Async: Sync vs Async Endpoints (Improved)

Builds on sync_vs_async.py by adding:
  - A "wrong" async endpoint that blocks the event loop
  - A /race/{mode} test endpoint that fires 3 concurrent requests
  - A /stress/{mode} test that fires 100 requests to reveal
    the threadpool bottleneck (THIS is where async wins)

Run:  uvicorn examples.07_async.sync_vs_async_improved:app --reload

Try these one at a time first:
  GET /sync        → runs in a threadpool (def + time.sleep)
  GET /async       → runs on the event loop (async def + await)
  GET /async-wrong → BLOCKS the event loop! (async def + time.sleep)

Small scale (3 requests — no difference):
  GET /race/sync        → ~2s
  GET /race/async       → ~2s
  GET /race/async-wrong → ~6s (blocked!)

Large scale (100 requests — async wins!):
  GET /stress/sync      → ~1.5s (threadpool bottleneck!)
  GET /stress/async     → ~0.5s ✅
"""

import asyncio
import time

from fastapi import FastAPI

app = FastAPI(title="Sync vs Async (Improved)")

DELAY = 2  # seconds — for the basic endpoints (long enough to feel)
STRESS_DELAY = 0.5  # seconds — shorter delay for stress test


# 1. Sync endpoint (correct)

@app.get("/sync")
def sync_endpoint():
    """
    Plain `def` — FastAPI runs this in a **threadpool**.
    Each request gets its own thread, so blocking calls
    like time.sleep() do NOT freeze the server.

    2-second delay, but concurrent requests run in parallel.
    """
    start = time.time()
    time.sleep(DELAY)  # blocking — but OK because it's in a thread
    elapsed = round(time.time() - start, 2)
    return {"style": "sync (def)", "delay": f"{elapsed}s", "note": "Ran in threadpool ✅"}


# 2. Async endpoint (correct)

@app.get("/async")
async def async_endpoint():
    """
    `async def` — runs directly on the **event loop**.
    Uses `await asyncio.sleep()` which is non-blocking.
    The event loop can handle other requests while this one waits.

    2-second delay, concurrent requests run in parallel.
    """
    start = time.time()
    await asyncio.sleep(DELAY)  # non-blocking — correct in async def
    elapsed = round(time.time() - start, 2)
    return {"style": "async (async def)", "delay": f"{elapsed}s", "note": "Ran on event loop ✅"}


# 3. Async endpoint (WRONG!)

@app.get("/async-wrong")
async def async_wrong_endpoint():
    """
    ⚠️ THE CLASSIC MISTAKE!

    This is `async def` but uses `time.sleep()` instead of
    `await asyncio.sleep()`. This BLOCKS the entire event loop!

    If 3 requests come at the same time:
      - /sync:        ~2s total  (parallel threads)
      - /async:       ~2s total  (parallel on event loop)
      - /async-wrong: ~6s total! (sequential — one blocks the others)
    """
    start = time.time()
    time.sleep(DELAY)  # ❌ BLOCKING call inside async def — freezes the server!
    elapsed = round(time.time() - start, 2)
    return {"style": "async WRONG", "delay": f"{elapsed}s", "note": "BLOCKED the event loop ❌"}


# 4. Race test — 3 requests (no visible difference between sync & async)

@app.get("/race/{mode}")
async def race(mode: str):
    """
    Fire 3 concurrent requests to the chosen endpoint and measure total time.

    Try:
      GET /race/sync        → ~2s (threads handle concurrency)
      GET /race/async       → ~2s (event loop handles concurrency)
      GET /race/async-wrong → ~6s (event loop was blocked!)
    """
    import httpx

    url_map = {
        "sync": "http://127.0.0.1:8000/sync",
        "async": "http://127.0.0.1:8000/async",
        "async-wrong": "http://127.0.0.1:8000/async-wrong",
    }

    if mode not in url_map:
        return {"error": f"Unknown mode '{mode}'. Use: sync, async, async-wrong"}

    url = url_map[mode]
    start = time.time()

    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            client.get(url, timeout=30),
            client.get(url, timeout=30),
            client.get(url, timeout=30),
        )

    total = round(time.time() - start, 2)

    return {
        "mode": mode,
        "concurrent_requests": 3,
        "total_time": f"{total}s",
        "expected": "~2s" if mode != "async-wrong" else "~6s (blocked!)",
        "responses": [r.json() for r in results],
    }


# 5. Lightweight endpoints for stress testing
# These use a shorter delay (0.5s) so the stress test finishes quickly.

@app.get("/light/sync")
def light_sync():
    """Lightweight sync endpoint (0.5s delay) for stress testing."""
    time.sleep(STRESS_DELAY)
    return {"ok": True}


@app.get("/light/async")
async def light_async():
    """Lightweight async endpoint (0.5s delay) for stress testing."""
    await asyncio.sleep(STRESS_DELAY)
    return {"ok": True}


# 6. Stress test — THIS is where async wins!

@app.get("/stress/{mode}")
async def stress(mode: str):
    """
    Fire 100 concurrent requests and compare total time.

    The default threadpool has only ~40 threads, so:
      - sync:  100 requests ÷ 40 threads = 3 batches × 0.5s = ~1.5s
      - async: 100 requests on 1 event loop = 1 batch × 0.5s = ~0.5s

    Try:
      GET /stress/sync   → ~1.5s  (threadpool bottleneck!)
      GET /stress/async  → ~0.5s  (event loop handles all 100 at once)

    THIS is why async matters at scale!
    """
    import httpx

    url_map = {
        "sync": "http://127.0.0.1:8000/light/sync",
        "async": "http://127.0.0.1:8000/light/async",
    }

    if mode not in url_map:
        return {"error": f"Unknown mode '{mode}'. Use: sync, async"}

    url = url_map[mode]
    n = 100
    start = time.time()

    async with httpx.AsyncClient() as client:
        tasks = [client.get(url, timeout=60) for _ in range(n)]
        results = await asyncio.gather(*tasks)

    total = round(time.time() - start, 2)

    success = sum(1 for r in results if r.status_code == 200)

    return {
        "mode": mode,
        "concurrent_requests": n,
        "successful": success,
        "total_time": f"{total}s",
        "expected": (
            "~1.5s (threadpool limit: 40 threads)"
            if mode == "sync"
            else "~0.5s (event loop)"
        ),
        "conclusion": (
            "⚠️ Sync hit the threadpool ceiling — requests had to wait in queue!"
            if mode == "sync"
            else "✅ Async handled all 100 requests simultaneously on one thread!"
        ),
    }
