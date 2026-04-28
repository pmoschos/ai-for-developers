"""
07 — Async: Background Tasks

Run:  uvicorn examples.07_async.background_tasks:app --reload

Try in /docs:
  POST /send-email?to=alice@example.com
  → Response returns immediately
  → Check terminal: background task runs after response
"""

from pathlib import Path

from fastapi import BackgroundTasks, FastAPI

app = FastAPI(title="Background Tasks")

LOG_FILE = Path("background_log.txt")


def write_log(message: str):
    """This runs AFTER the response is sent to the client."""
    with open(LOG_FILE, "a") as f:
        f.write(message + "\n")
    print(f"  [BG] Logged: {message}")


@app.post("/send-email")
def send_email(to: str, bg: BackgroundTasks):
    """
    BackgroundTasks runs fire-and-forget work after the response.
    The client gets an immediate response; the log write happens later.

    For heavier jobs, use Celery, RQ, or Dramatiq instead.
    """
    bg.add_task(write_log, f"Email sent to {to}")
    return {"status": "queued", "to": to}
