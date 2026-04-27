"""
04 — Responses: Custom Response Types

This example demonstrates that FastAPI endpoints do not have to return JSON.
You can explicitly choose a different response type depending on the use case.

Covered concepts:
1. Plain text responses
   Useful for simple text output, health checks, or lightweight endpoints.

2. HTML responses
   Useful when returning raw HTML content directly from an endpoint.

3. Personalised HTML responses
   Demonstrates combining path and query parameters with HTML output.

4. Redirect responses
   Useful when sending the client to another route or URL.

5. File responses
   Serve a file from disk as a download, with a 404 fallback.

6. Streaming responses
   Stream content chunk by chunk — both instant and delayed (async).

7. response_class
   Tells FastAPI how to serialize the returned content and how to document
   the endpoint in OpenAPI.

Run:
    uvicorn examples.04_responses.custom_responses:app --reload

Alternative:
    fastapi dev custom_responses.py

Open API docs:
    http://localhost:8000/docs

Try:
    GET /hello
        -> plain text response

    GET /home
        -> HTML page

    GET /greet/Alice?title=Dr
        -> personalised HTML greeting

    GET /go
        -> redirect to /docs

    GET /download/some_file.pdf
        -> file download (404 if missing)

    GET /stream
        -> streamed lines (instant burst)

    GET /countdown
        -> live countdown, one number per second
"""

import asyncio
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    PlainTextResponse,
    RedirectResponse,
    StreamingResponse,
)

# Create the FastAPI application instance.
# Its metadata appears in the generated Swagger/OpenAPI docs.
app = FastAPI(
    title="Custom Response Types",
    description=(
        "Demonstrates plain text, HTML, file, streaming, "
        "and redirect responses in FastAPI."
    ),
    version="1.0.0",
)


# ── Plain Text ──────────────────────────────────────────────────────────


@app.get(
    "/hello",
    response_class=PlainTextResponse,
    summary="Return plain text",
    description=(
        "Returns a plain text response instead of the default JSON response."
    ),
    tags=["Responses"],
)
def hello():
    """
    Return plain text content.

    By default, FastAPI usually returns JSON responses.
    Here, `response_class=PlainTextResponse` tells FastAPI to send the
    returned string as plain text with an appropriate content type.

    This is useful for:
    - simple text endpoints,
    - lightweight status messages,
    - plain-text integrations.
    """
    return PlainTextResponse("Hello, plain text!")


# ── HTML ────────────────────────────────────────────────────────────────


@app.get(
    "/home",
    response_class=HTMLResponse,
    summary="Return raw HTML",
    description=(
        "Returns an HTML document directly from the endpoint."
    ),
    tags=["Responses"],
)
def home():
    """
    Return raw HTML content.

    `response_class=HTMLResponse` tells FastAPI to treat the returned string
    as HTML rather than JSON or plain text.

    This is useful for:
    - small demo pages,
    - dynamically generated HTML,
    - simple web responses without a template engine.

    Note:
    For larger applications, HTML is often rendered using a template system
    such as Jinja2 rather than hardcoding markup inside the route.
    """
    html = """
    <html>
        <head><title>Home</title></head>
        <body>
            <h1>Welcome to FastAPI</h1>
            <p>This is an HTML response.</p>
        </body>
    </html>
    """
    return HTMLResponse(content=html)


# ── Personalised HTML ───────────────────────────────────────────────────


@app.get(
    "/greet/{name}",
    response_class=HTMLResponse,
    summary="Return a personalised HTML greeting",
    description=(
        "Generates an HTML page that greets the user by name. "
        "An optional `title` query parameter is also supported."
    ),
    tags=["Responses"],
)
def greet(name: str, title: str | None = None):
    """
    Return a personalised HTML greeting using path + query params.

    Path parameter:
    - `name` (required): the person's name.

    Query parameter:
    - `title` (optional): a prefix such as Dr, Prof, Mr, etc.

    Example:
        GET /greet/Alice?title=Dr  →  "Hello, Dr Alice!" in HTML.

    This endpoint shows that HTML responses can be dynamic,
    incorporating user-supplied data directly into the markup.
    """
    display = f"{title} {name}" if title else name
    html = f"""
    <html>
        <head><title>Greeting</title></head>
        <body>
            <h1>Hello, {display}!</h1>
            <p>This HTML was generated with a <b>path</b> parameter
               and an optional <b>query</b> parameter.</p>
        </body>
    </html>
    """
    return HTMLResponse(content=html)


# ── Redirect ────────────────────────────────────────────────────────────


@app.get(
    "/go",
    summary="Redirect to the documentation page",
    description=(
        "Returns a redirect response that sends the client to /docs."
    ),
    tags=["Responses"],
)
def go():
    """
    Redirect the client to another endpoint.

    `RedirectResponse` tells the client to make a new request to a different URL.

    In this example:
    - the client is redirected to `/docs`
    - status code 307 is used

    Why 307?
    A 307 Temporary Redirect preserves the original HTTP method when the
    redirect is followed. For a simple GET route like this one, it behaves
    similarly to other temporary redirects, but it is more precise.
    """
    return RedirectResponse("/docs", status_code=307)


# ── File Download ───────────────────────────────────────────────────────


@app.get(
    "/download/{filename}",
    response_class=FileResponse,
    summary="Download a file by name",
    description=(
        "Serves a file from the application directory as a browser download. "
        "Returns 404 if the file does not exist."
    ),
    tags=["Responses"],
)
def download(filename: str):
    """
    Serve the requested file as a download, or return 404 if missing.

    Path parameter:
    - `filename` (required): name of the file to download.

    Example:
        GET /download/some_file.pdf

    Security note:
    `Path(filename).name` strips any directory traversal characters
    (e.g. `../../etc/passwd` → `passwd`), so the endpoint only ever
    looks inside its own directory.

    The file is resolved relative to the script's parent directory using
    `Path(__file__).parent`, making it work regardless of where uvicorn
    is launched from.
    """
    safe_name = Path(filename).name          # strip any path traversal
    file_path = Path(__file__).parent.parent / safe_name
    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail=f"File '{safe_name}' not found",
        )
    return FileResponse(path=file_path, filename=safe_name)


# ── Streaming ───────────────────────────────────────────────────────────


@app.get(
    "/stream",
    summary="Stream data line by line (instant)",
    description=(
        "Returns a streaming response that sends 10 lines of text. "
        "All lines arrive as fast as possible (synchronous generator)."
    ),
    tags=["Responses"],
)
def stream():
    """
    Stream content chunk by chunk using a synchronous generator.

    `StreamingResponse` accepts any iterable or generator. Here a simple
    `yield`-based generator produces 10 lines of text that are sent to the
    client as they are generated.

    This is useful for:
    - large datasets that should not be buffered entirely in memory,
    - CSV exports,
    - log file tailing.
    """
    def generate():
        for i in range(10):
            yield f"Line {i}\n"
    return StreamingResponse(generate(), media_type="text/plain")


@app.get(
    "/countdown",
    summary="Stream a live countdown (one number per second)",
    description=(
        "Returns an async streaming response that counts down from 10 to 1 "
        "with a one-second delay between each number."
    ),
    tags=["Responses"],
)
async def countdown():
    """
    Stream a live countdown — one number per second.

    This endpoint uses an **async generator** combined with
    `asyncio.sleep` to introduce a real delay between chunks.
    Open it in a browser tab to see data arrive progressively.

    Unlike `/stream` (which sends everything at once), this endpoint
    demonstrates *true* server-push streaming where the client receives
    partial content over time.

    This pattern is the foundation for:
    - Server-Sent Events (SSE),
    - real-time progress indicators,
    - AI/LLM token-by-token responses.
    """
    async def tick():
        for i in range(10, 0, -1):
            yield f"{i}...\n"
            await asyncio.sleep(1)
        yield "BooooooooOOOOOOOOOOMMMMMMMMMMM! 🚀\n"
    return StreamingResponse(tick(), media_type="text/plain")