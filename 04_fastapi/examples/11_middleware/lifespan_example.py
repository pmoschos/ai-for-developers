"""
11 — Middleware: Lifespan Events (Startup / Shutdown)

Run:
    uvicorn examples.11_middleware.lifespan_example:app --reload

Watch the terminal for startup/shutdown messages.

What this example shows:
- how to run code once when the app starts
- how to run cleanup code once when the app shuts down
- how to store shared resources in `app.state`
- how to access those shared resources inside request handlers

The shared httpx client is available at:
    request.app.state.http
"""

from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager.

    FastAPI calls this once for the whole application lifecycle.

    Execution model:
    - Code BEFORE `yield` runs during application startup
    - Code AFTER `yield` runs during application shutdown

    This is a good place to create and later clean up shared resources, such as:
    - HTTP clients
    - database connection pools
    - cache clients
    - ML models
    - reusable service objects
    """

    # -------------------------
    # STARTUP PHASE
    # -------------------------
    # Create one shared async HTTP client for the whole app.
    #
    # Why do this here?
    # - avoids creating a new client on every request
    # - allows connection reuse / pooling
    # - keeps setup centralized
    app.state.http = httpx.AsyncClient()

    # app.state is a generic container attached to the FastAPI app instance.
    # It is commonly used to store shared objects initialized at startup.
    print("App ready [OK]  (httpx client created)")

    # Yield control back to FastAPI.
    # After this point, the application starts serving requests.
    yield

    # -------------------------
    # SHUTDOWN PHASE
    # -------------------------
    # Close the shared HTTP client gracefully.
    #
    # This is important because async clients may hold:
    # - open connections
    # - connection pools
    # - transport resources
    await app.state.http.aclose()
    print("Bye  (httpx client closed)")


# Register the lifespan manager in the FastAPI app.
# FastAPI will automatically call it on startup and shutdown.
app = FastAPI(
    title="Lifespan Events",
    lifespan=lifespan,
)


@app.get("/")
def root():
    """
    Simple endpoint used to verify that the app is running.
    """
    return {"message": "App is running with lifespan events"}


@app.get("/joke")
async def joke(request: Request):
    """
    Fetch a random joke using the shared httpx client stored in app.state.

    `request.app` gives access to the FastAPI application instance
    handling the current request.

    Since the shared client was created at startup as:
        app.state.http = httpx.AsyncClient()

    we can reuse it here instead of creating a new client every time.
    """

    # Make an outbound HTTP request using the shared async client.
    # This call must be awaited because AsyncClient is asynchronous.
    r = await request.app.state.http.get(
        "https://official-joke-api.appspot.com/random_joke"
    )

    # The API returns JSON like:
    # {"type": "general", "setup": "...", "punchline": "...", "id": 123}
    data = r.json()

    return {
        "Q": data["setup"],
        "A": data["punchline"],
    }