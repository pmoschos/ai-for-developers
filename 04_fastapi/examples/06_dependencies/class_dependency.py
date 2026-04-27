"""
06 — Dependencies: Class-Based Dependency

Run:  uvicorn examples.06_dependencies.class_dependency:app --reload

Try:
  GET /items?skip=5&limit=3
"""

from typing import Annotated

from fastapi import Depends, FastAPI

app = FastAPI(title="Class Dependencies")

fake_items = [{"name": f"Item {i}"} for i in range(100)]


class Pager:
    """A class dependency gives you typed attributes instead of a dict."""

    def __init__(self, skip: int = 0, limit: int = 10):
        self.skip = skip
        self.limit = limit


@app.get("/items")
def list_items(p: Annotated[Pager, Depends()]):
    """
    Depends() with no argument uses the type hint (Pager) as the dependency.
    FastAPI creates a Pager instance with query params as constructor args.
    """
    return fake_items[p.skip: p.skip + p.limit]
