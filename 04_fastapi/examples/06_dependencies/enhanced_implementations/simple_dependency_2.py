"""
06 — Dependencies: Simple Function Dependency

This example demonstrates one of FastAPI's most useful design features:
dependencies.

Covered concepts:
1. Reusable dependency functions
   A normal Python function can be used to extract, validate, or prepare data
   before an endpoint runs.

2. Depends(...)
   Tells FastAPI to call another function and inject its result.

3. Shared logic across endpoints
   Multiple routes can reuse the same dependency to avoid duplication.

4. Annotated aliases
   A type alias can make endpoint signatures cleaner and easier to read.

Run:
    uvicorn examples.06_dependencies.simple_dependency:app --reload

Alternative:
    fastapi dev simple_dependency.py

Open API docs:
    http://localhost:8000/docs

Try:
    GET /items?skip=10&limit=5
    GET /users?limit=3
"""

from typing import Annotated

from fastapi import Depends, FastAPI, Query

# Create the FastAPI application instance.
# Its metadata appears in the generated Swagger/OpenAPI docs.
app = FastAPI(
    title="Simple Dependencies",
    description=(
        "Demonstrates how to reuse query-parameter extraction logic with "
        "a simple FastAPI dependency."
    ),
    version="1.0.0",
)

# Fake in-memory data used only for demonstration.
fake_items = [{"name": f"Item {i}"} for i in range(100)]
fake_users = [{"name": f"User {i}"} for i in range(50)]


def pagination(
    skip: Annotated[
        int,
        Query(
            description="Number of records to skip",
            examples=[10],
            ge=0,
        ),
    ] = 0,
    limit: Annotated[
        int,
        Query(
            description="Maximum number of records to return",
            examples=[5],
            ge=1,
            le=100,
        ),
    ] = 10,
):
    """
    Reusable dependency that extracts pagination parameters.

    Because this function is used with `Depends(...)`, FastAPI treats its
    parameters like normal request parameters and validates them automatically.

    In this example:
    - `skip` controls the starting offset
    - `limit` controls how many records are returned

    The returned dictionary becomes the injected value received by the endpoint.
    """
    return {
        "skip": skip,
        "limit": limit,
    }


# Create a reusable type alias for dependency injection.
# This keeps endpoint signatures shorter and more readable.
Page = Annotated[dict, Depends(pagination)]


@app.get(
    "/items",
    summary="List items using shared pagination dependency",
    description=(
        "Uses the `pagination` dependency to read and validate `skip` and "
        "`limit` query parameters, then returns a slice of the item list."
    ),
    tags=["Items"],
)
def list_items(page: Page):
    """
    Return a paginated slice of fake items.

    The `page` argument is not provided directly by the client.
    Instead, FastAPI resolves it through the `pagination` dependency.

    This means:
    - FastAPI reads `skip` and `limit` from the query string
    - validates them
    - calls `pagination(...)`
    - injects the returned dictionary into `page`

    Example:
        GET /items?skip=10&limit=5

    Then inside the function:
        page == {"skip": 10, "limit": 5}
    """
    return {
        "skip": page["skip"],
        "limit": page["limit"],
        "count": len(fake_items[page["skip"]: page["skip"] + page["limit"]]),
        "items": fake_items[page["skip"]: page["skip"] + page["limit"]],
    }


@app.get(
    "/users",
    summary="List users using the same shared pagination dependency",
    description=(
        "Reuses the same pagination dependency as the /items endpoint. "
        "This avoids duplicating the same query-parameter logic."
    ),
    tags=["Users"],
)
def list_users(page: Page):
    """
    Return a paginated slice of fake users.

    This endpoint uses exactly the same `Page` dependency alias as `/items`.

    That is the key idea:
    one dependency function can be reused across multiple endpoints,
    keeping the code DRY and consistent.

    Example:
        GET /users?limit=3

    Then inside the function:
        page == {"skip": 0, "limit": 3}
    """
    return {
        "skip": page["skip"],
        "limit": page["limit"],
        "count": len(fake_users[page["skip"]: page["skip"] + page["limit"]]),
        "users": fake_users[page["skip"]: page["skip"] + page["limit"]],
    }