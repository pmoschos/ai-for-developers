"""
02 — Query Parameters: Basics, Defaults, Optional

This example introduces the most common FastAPI query parameter patterns:

1. Basic query parameters
   Any function parameter not declared in the path is treated as a query parameter.

2. Default values
   A default value makes a query parameter optional.

3. Optional parameters with validation
   Query(...) lets you attach validation rules and documentation metadata.

4. Automatic type conversion
   FastAPI converts incoming query string values to Python types based on type hints.

Run:
    uvicorn examples.02_parameters.query_params:app --reload

Alternative:
    fastapi dev query_params.py

Open API docs:
    http://localhost:8000/docs

Try:
    GET /items
        -> skip=0, limit=10

    GET /items?limit=5
        -> skip=0, limit=5

    GET /items?skip=20&limit=5

    GET /search?q=fastapi&in_stock=true

    GET /search
        -> q=None
"""

# To run this code:
# fastapi dev query_params.py
# or
# uvicorn query_params:app --reload
# To view the Swagger UI documentation:
# http://localhost:8000/docs

from typing import Annotated

from fastapi import FastAPI, Query

# Create the FastAPI application instance.
# The metadata below appears in the generated Swagger/OpenAPI docs.
app = FastAPI(
    title="Query Parameters",
    description=(
        "Demonstrates basic query parameters, default values, optional "
        "parameters, and validation using Query(...)."
    ),
    version="1.0.0",
)

# Fake data used only for demonstration.
# In a real application, these items would usually come from a database.
fake_items = [{"name": f"Item {i}"} for i in range(100)]


@app.get(
    "/items",
    summary="List items with pagination-style query parameters",
    description=(
        "Uses `skip` and `limit` as query parameters. Since they are not part "
        "of the URL path, FastAPI treats them as query parameters automatically."
    ),
    tags=["Items"],
)
def list_items(skip: int = 0, limit: int = 10):
    """
    Return a slice of the fake items list.

    Key idea:
    Any function parameter that is not part of the path is interpreted
    by FastAPI as a query parameter.

    Here:
    - `skip` defaults to 0
    - `limit` defaults to 10

    Because both have default values, they are optional.

    Example requests:
        /items
        /items?limit=5
        /items?skip=20&limit=5

    FastAPI also converts query string values automatically:
        ?skip=20   -> int
        ?limit=5   -> int
    """
    return {
        "skip": skip,
        "limit": limit,
        "count": len(fake_items[skip: skip + limit]),
        "items": fake_items[skip: skip + limit],
    }


@app.get(
    "/search",
    summary="Search items with optional validated query parameters",
    description=(
        "Demonstrates optional query parameters, string validation, "
        "default values, and boolean parsing."
    ),
    tags=["Search"],
)
def search(
    q: Annotated[
        str | None,
        Query(
            min_length=3,
            max_length=50,
            description="Search query string",
            examples=["fastapi"],
        ),
    ] = None,
    category: Annotated[
        str,
        Query(
            description="Category to search in. Defaults to 'all'.",
            examples=["books"],
        ),
    ] = "all",
    in_stock: Annotated[
        bool,
        Query(
            description="Whether to return only in-stock items.",
            examples=[True],
        ),
    ] = False,
):
    """
    Return validated search filters.

    Parameters:
    - `q`
      Optional search text.
      Because its default is None, it is not required.
      If provided, it must:
      - have at least 3 characters
      - have at most 50 characters

    - `category`
      A regular query parameter with a default value of "all".

    - `in_stock`
      A boolean query parameter.
      FastAPI converts common string values such as:
      true / false
      1 / 0
      yes / no
      on / off

    Example requests:
        /search
        /search?q=fastapi
        /search?q=python&category=books
        /search?q=api&in_stock=true
    """
    return {
        "q": q,
        "category": category,
        "in_stock": in_stock,
        "types": {
            "q": type(q).__name__ if q is not None else None,
            "category": type(category).__name__,
            "in_stock": type(in_stock).__name__,
        },
    }
