"""
13 — Advanced: Static Files & Jinja2 Templates

Run from anywhere:
    uvicorn examples.13_advanced.static_templates:app --reload
    uvicorn static_templates:app --reload

Try:
  GET /page/Alice → rendered HTML template
  GET /static/style.css → static CSS file
"""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Resolve directories relative to THIS file, not the working directory.
# This ensures the app works regardless of where you run uvicorn from.
BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Static Files & Templates")

# Serve static files (CSS, JS, images) from the "static" directory
app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

# Configure Jinja2 templates directory
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/page/{name}")
def page(name: str, request: Request):
    """
    Render an HTML template with Jinja2.
    The 'request' object is required by Jinja2Templates.
    """
    return templates.TemplateResponse(
        name="hello.html",
        request=request,
        context={"name": name},
    )
