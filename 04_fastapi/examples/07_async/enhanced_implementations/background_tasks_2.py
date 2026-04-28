"""
07 — Async: Background Tasks

This example demonstrates how to run small follow-up tasks after the HTTP
response has already been sent to the client.

Covered concepts:
1. BackgroundTasks
   FastAPI can schedule lightweight background work that runs after the
   response is returned.

2. Immediate response
   The client does not wait for the background task to finish.

3. Fire-and-forget behavior
   Useful for small side effects such as logging, notifications, or simple
   post-processing steps.

4. Limits of BackgroundTasks
   This mechanism is convenient for lightweight in-process work, but it is
   not a replacement for a real job queue for heavy or critical tasks.

Run:
    uvicorn examples.07_async.background_tasks:app --reload

Alternative:
    fastapi dev background_tasks.py

Open API docs:
    http://localhost:8000/docs

Try in /docs:
    POST /send-email?to=alice@example.com

Expected behavior:
    - The HTTP response returns immediately
    - The background task runs afterward
    - Check the terminal and log file to observe the side effect
"""

from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, Query

# Create the FastAPI application instance.
# Its metadata appears in the generated Swagger/OpenAPI docs.
app = FastAPI(
    title="Background Tasks",
    description=(
        "Demonstrates how to schedule lightweight post-response work using "
        "FastAPI BackgroundTasks."
    ),
    version="1.0.0",
)

# Log file used only for demonstration.
# Each background task appends a line to this file.
LOG_FILE = Path("background_log.txt")


def write_log(message: str):
    """
    Background task function that writes a message to a log file.

    Important behavior:
    This function is not executed before the response is returned.
    Instead, it is scheduled by FastAPI and runs after the response has
    already been sent to the client.

    This makes it suitable for lightweight side effects such as:
    - logging
    - sending a simple notification
    - appending audit records
    - lightweight cleanup or post-processing
    """
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")

    print(f"  [BG] Logged: {message}")


@app.post(
    "/send-email",
    summary="Queue a lightweight background task after the response",
    description=(
        "Simulates sending an email by scheduling a background log write. "
        "The client receives an immediate response, while the background task "
        "runs afterward."
    ),
    tags=["Background Tasks"],
)
def send_email(
    to: str = Query(
        ...,
        description="Recipient email address",
        examples=["alice@example.com"],
    ),
    bg: BackgroundTasks = None,
):
    """
    Schedule a background task after returning the response.

    FastAPI injects a `BackgroundTasks` object into the endpoint.
    You can register one or more tasks using `bg.add_task(...)`.

    In this example:
    - the endpoint returns immediately with status information
    - the background task appends a line to a log file afterward

    Key idea:
    The API response and the background action are decoupled in time.

    This pattern is useful when:
    - the client does not need to wait for the side effect
    - the work is small and quick
    - occasional in-process execution is acceptable

    For heavier or more reliable asynchronous workloads, a dedicated
    background worker system such as Celery, RQ, or Dramatiq is usually
    a better choice.
    """
    bg.add_task(write_log, f"Email sent to {to}")

    return {
        "status": "queued",
        "to": to,
        "note": "The background task will run after the response is sent.",
    }