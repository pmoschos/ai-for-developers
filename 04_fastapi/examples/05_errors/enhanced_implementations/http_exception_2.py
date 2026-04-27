"""
05 — Error Handling: HTTPException

This example demonstrates the standard FastAPI way to return an HTTP error
from inside an endpoint: raising HTTPException.

Covered concepts:
1. Raising HTTPException
   Instead of returning an error manually, you raise an exception.

2. Status codes
   The exception includes the HTTP status code to send to the client.

3. Error details
   The `detail` field becomes part of the JSON error response.

4. Custom headers
   Optional headers can be included in the error response.

Run:
    uvicorn examples.05_errors.http_exception:app --reload

Alternative:
    fastapi dev http_exception.py

Open API docs:
    http://localhost:8000/docs

Try:
    GET /items/a
        -> 200 OK
        -> {"key": "a", "name": "Apple"}

    GET /items/x
        -> 404 Not Found
        -> {"detail": "Item 'x' not found"}
"""

from fastapi import FastAPI, HTTPException, status

# Create the FastAPI application instance.
# Its metadata appears in the generated Swagger/OpenAPI docs.
app = FastAPI(
    title="HTTPException",
    description=(
        "Demonstrates how to raise HTTPException in FastAPI to return "
        "structured HTTP error responses."
    ),
    version="1.0.0",
)

# Simple in-memory data store for demonstration.
# Keys act like item IDs, values are item names.
items = {
    "a": "Apple",
    "b": "Banana",
    "c": "Cherry",
}


@app.get(
    "/items/{key}",
    summary="Get an item by key or raise 404",
    description=(
        "Returns an item if the given key exists. Otherwise raises "
        "HTTPException with status 404."
    ),
    tags=["Items"],
)
def get_item(key: str):
    """
    Return an item by key.

    If the key does not exist, raise `HTTPException`.
    FastAPI catches it automatically and converts it into a proper
    HTTP error response.

    Important idea:
    You do not manually build an error response object here.
    You simply raise an exception with the appropriate metadata.

    In this example:
    - `status_code=404` means the resource was not found
    - `detail=...` becomes the JSON error message
    - `headers={...}` adds an optional custom HTTP header

    Example success:
        GET /items/a
        -> {"key": "a", "name": "Apple"}

    Example failure:
        GET /items/x
        -> 404
        -> {"detail": "Item 'x' not found"}
    """
    if key not in items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item '{key}' not found",
            headers={"X-Error": "item-missing"},  # optional custom response header
        )

    return {
        "key": key,
        "name": items[key],
    }