"""
14 — Deployment: Structured Logging

Run:
    uvicorn logging_demo:app --reload

What this file teaches:
    - How to set up structured JSON logging for production
    - How to add request IDs to every log entry
    - How to log request/response metadata via middleware
    - Why structured logs matter for log aggregation tools

Key idea:
    In production, plain text logs like print("user created")
    are hard to search and filter. Structured JSON logs let tools
    like ELK, Datadog, and CloudWatch parse and query fields like
    request_id, method, path, status_code, and duration.
"""

import logging
import time
import uuid

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# ============================================================================
# Logging Setup
# ============================================================================

# Configure the Python logger to output structured information.
# In production, you would typically use python-json-logger
# or structlog for proper JSON output.

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("api")


# ============================================================================
# Request Logging Middleware
# ============================================================================

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs every request with timing and a unique ID.

    Each request gets a UUID attached via the X-Request-ID header.
    This makes it easy to trace a single request through your logs,
    especially in distributed systems.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Generate a unique ID for this request.
        request_id = str(uuid.uuid4())[:8]

        # Record the start time.
        start = time.perf_counter()

        # Process the request.
        response = await call_next(request)

        # Calculate processing time.
        duration_ms = (time.perf_counter() - start) * 1000

        # Log the request details.
        logger.info(
            "request_id=%s method=%s path=%s status=%d duration=%.1fms",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

        # Attach the request ID to the response headers.
        # Clients can use this to reference specific requests in bug reports.
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{duration_ms:.1f}ms"

        return response


# ============================================================================
# App
# ============================================================================

app = FastAPI(title="Structured Logging Demo")

app.add_middleware(RequestLoggingMiddleware)


@app.get("/")
def root():
    """Root endpoint."""
    logger.info("Root endpoint called")
    return {"message": "Check your terminal for structured logs"}


@app.get("/users/{user_id}")
def get_user(user_id: int):
    """Simulated user lookup with logging."""
    logger.info("Looking up user_id=%d", user_id)

    if user_id > 100:
        logger.warning("User not found: user_id=%d", user_id)
        return {"error": "User not found"}

    logger.info("User found: user_id=%d", user_id)
    return {"user_id": user_id, "name": f"User {user_id}"}


@app.get("/error")
def trigger_error():
    """Endpoint that deliberately raises an error for logging demonstration."""
    logger.error("Deliberate error triggered for demonstration")
    raise ValueError("This is a test error")
