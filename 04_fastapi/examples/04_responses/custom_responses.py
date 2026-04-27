"""
04 — Responses: Custom Response Types

Run:  uvicorn examples.04_responses.custom_responses:app --reload

Try:
  GET /hello              → plain text
  GET /home               → HTML page
  GET /greet/Alice?title=Dr → personalised HTML greeting
  GET /go                 → redirect to /docs
"""

import asyncio
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import (
    HTMLResponse,
    PlainTextResponse,
    RedirectResponse,
    FileResponse, 
    StreamingResponse
)

app = FastAPI(title="Custom Response Types")


@app.get("/hello", response_class=PlainTextResponse)
def hello():
    """Return plain text instead of JSON."""
    return "Hello, plain text!"
    # return PlainTextResponse("Hello, plain text!")


@app.get("/home", response_class=HTMLResponse)
def home():
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


@app.get("/greet/{name}", response_class=HTMLResponse)
def greet(name: str, title: str | None = None):
    """Return a personalised HTML greeting using path + query params.
    Example: GET /greet/Alice?title=Dr → "Hello, Dr Alice!" in HTML.
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


@app.get("/go")
def go():
    """Redirect to the Swagger docs."""
    return RedirectResponse("/docs", status_code=307)


@app.get("/download/{filename}", response_class=FileResponse)
def download(filename: str):
    """Serve the requested file as a download, or 404 if missing.
    Example: GET /download/some_file.pdf
    """
    safe_name = Path(filename).name          # strip any path traversal
    file_path = Path(__file__).parent / safe_name
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail=f"File '{safe_name}' not found")
    return FileResponse(path=file_path, filename=safe_name)


# Stream content chunk by chunk
@app.get("/stream")
def stream():
    """Stream data line by line (instant burst)."""
    def generate():
        for i in range(10):
            yield f"Line {i}\n"
    return StreamingResponse(generate(), media_type="text/plain")


@app.get("/countdown")
async def countdown():
    """Stream a live countdown — one number per second.
    Open in a browser tab to see data arrive progressively.
    """
    async def tick():
        for i in range(10, 0, -1):
            yield f"{i}...\n"
            await asyncio.sleep(1)
        yield "BooooooooOOOOOOOOOOMMMMMMMMMMM! 🚀 \n"
    return StreamingResponse(tick(), media_type="text/plain")