# 14 — Deployment

Practical examples covering production-readiness patterns for FastAPI.

## Files

| File | What It Teaches |
|------|-----------------|
| `health_check.py` | `/health` and `/health/ready` endpoints for load balancers and Kubernetes |
| `settings_demo.py` | Environment variables with pydantic-settings, `.env` files, conditional docs |
| `logging_demo.py` | Structured logging, request IDs, timing middleware |
| `Dockerfile.reference` | Annotated production Dockerfile with detailed comments |

## How to Run

```bash
# From this directory (examples/14_deployment/)
uvicorn health_check:app --reload
uvicorn settings_demo:app --reload
uvicorn logging_demo:app --reload
```

## Docker (from the repo root)

```bash
docker build -t fastapi-tutorial .
docker run -d -p 8000:8000 fastapi-tutorial
```

## Running in Production

```bash
# Single process, reload OFF
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Multiple workers (good default: 2 x CPU cores + 1)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Gunicorn with Uvicorn workers (Linux only) — process manager + auto-restarts
gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000 app.main:app
```

## Production Checklist

- [ ] Secrets in env vars, not in code
- [ ] HTTPS via reverse proxy (Nginx, Caddy, cloud LB)
- [ ] CORS locked down — exact origins only
- [ ] Alembic for DB migrations (not create_all)
- [ ] Structured logging + /health endpoint
- [ ] Consider disabling /docs in production
- [ ] Workers tuned: (2 x CPU) + 1
- [ ] Database backups + tested restores

See `docs/14_deployment.md` for the theory.
