"""
11 — Middleware: Custom Middleware (Timing + Request ID)

Run:  uvicorn examples.11_middleware.custom_middleware:app --reload

Check response headers for:
  X-Process-Time: 0.0012
  X-Request-ID:   abc123-...
"""

import time
import uuid

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

app = FastAPI(title="Custom Middleware")


class TimingMiddleware(BaseHTTPMiddleware):
    """Add processing time and request ID to every response."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        start = time.perf_counter()

        response = await call_next(request)

        elapsed = time.perf_counter() - start
        response.headers["X-Process-Time"] = f"{elapsed:.4f}"
        response.headers["X-Request-ID"] = request_id
        return response


# Register the middleware
app.add_middleware(TimingMiddleware)


@app.get("/")
def root():
    return {"message": "Check the response headers!"}


@app.get("/slow")
def slow():
    """A deliberately slow endpoint to see timing in action."""
    time.sleep(0.5)
    return {"message": "That was slow"}
