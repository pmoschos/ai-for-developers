"""
14 — Deployment: Health Check Endpoint

Run:
    uvicorn health_check:app --reload

What this file teaches:
    - How to add a /health endpoint for load balancers and container orchestrators
    - What information to expose in a health response
    - Why this is essential for production deployments

Key idea:
    Every production API needs a /health endpoint that returns 200
    when the app is alive. Container orchestrators (Docker, Kubernetes),
    reverse proxies (Nginx, Caddy), and cloud load balancers use this
    to decide if your instance can receive traffic.
"""

from datetime import datetime, timezone

from fastapi import FastAPI

app = FastAPI(title="Health Check Demo")

# Store the startup time for uptime calculation.
STARTED_AT = datetime.now(timezone.utc)


@app.get("/")
def root():
    """Root endpoint with link to docs."""
    return {"message": "Health Check Demo", "docs": "/docs"}


@app.get("/health")
def health():
    """
    Health check endpoint.

    Returns basic information about the running service.
    Load balancers and orchestrators call this endpoint to verify
    the app is alive and ready to serve traffic.

    A minimal health check returns just {"status": "ok"}.
    In practice, you may also check database connectivity,
    cache availability, or external service health.
    """
    now = datetime.now(timezone.utc)
    uptime = now - STARTED_AT

    return {
        "status": "ok",
        "uptime_seconds": round(uptime.total_seconds()),
        "timestamp": now.isoformat(),
    }


@app.get("/health/ready")
def readiness():
    """
    Readiness probe.

    Kubernetes distinguishes between:
    - Liveness: Is the process alive? (/health)
    - Readiness: Can the process accept traffic? (/health/ready)

    A readiness probe might check:
    - database connectivity
    - cache connectivity
    - required external services

    For this demo, we always return ready.
    """
    return {"ready": True}
