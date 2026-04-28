# import os
# os.environ["ANYIO_MAX_THREADS"] = "20"  # limit threadpool to 20 (default is 40)

import asyncio
import time

from fastapi import FastAPI

app = FastAPI(title="Sync vs Async (Improved)")

DELAY = 2  # seconds — for the basic endpoints (long enough to feel)
STRESS_DELAY = 1  # seconds — for stress test (bigger gap in results)


@app.get("/sync")
def sync_endpoint():
    start = time.time()
    time.sleep(DELAY)  
    elapsed = round(time.time() - start, 2)
    return {"style": "sync (def)", "delay": f"{elapsed}s", "note": "Ran in threadpool ✅"}


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

@app.get("/stress/{mode}")
async def stress(mode: str):
    """
    This endpoint demonstrates the difference between sync and async endpoints
    by firing 200 concurrent requests to both.
    """
    import httpx

    url_map = {
        "sync": "http://127.0.0.1:8000/light/sync",
        "async": "http://127.0.0.1:8000/light/async",
    }

    if mode not in url_map:
        return {"error": f"Unknown mode '{mode}'. Use: sync, async"}

    url = url_map[mode]
    # Windows select() limit = 512 fds. Client + server share this process,
    # so each connection uses ~2 fds. Keep n under ~200 to stay safe.
    n = 200
    start = time.time()

    # Raise httpx connection limit so the ONLY bottleneck is the server threadpool (40 threads)
    limits = httpx.Limits(max_connections=n, max_keepalive_connections=n)

    async with httpx.AsyncClient(limits=limits) as client:
        tasks = [client.get(url, timeout=120) for _ in range(n)]
        results = await asyncio.gather(*tasks)

    total = round(time.time() - start, 2)

    success = sum(1 for r in results if r.status_code == 200)

    return {
        "mode": mode,
        "concurrent_requests": n,
        "successful": success,
        "total_time": f"{total}s",
        "conclusion": (
            "Sync hit the threadpool ceiling — requests had to wait in queue!"
            if mode == "sync"
            else "Async handled all 100 requests simultaneously on one thread!"
        ),
    }
