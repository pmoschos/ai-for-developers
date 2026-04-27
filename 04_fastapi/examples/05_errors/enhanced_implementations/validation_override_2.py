"""
05 — Error Handling: Override Validation Errors

This example demonstrates how to override FastAPI's default validation
error response for request parsing and type-conversion failures.

Covered concepts:
1. RequestValidationError
   FastAPI raises this when incoming request data fails validation.

2. Global exception override
   You can register a custom handler that replaces the default 422 response.

3. Custom error payload shape
   Useful when your frontend or API clients expect a specific error format.

4. Error normalization
   The handler can transform FastAPI/Pydantic validation details into a
   simpler and more consistent structure.

Run:
    uvicorn examples.05_errors.validation_override:app --reload

Alternative:
    fastapi dev validation_override.py

Open API docs:
    http://localhost:8000/docs

Try:
    GET /items/123
        -> 200 OK
        -> {"item_id": 123}

    GET /items/abc
        -> 400 Bad Request
        -> custom JSON validation error
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Create the FastAPI application instance.
# Its metadata appears in the generated Swagger/OpenAPI docs.
app = FastAPI(
    title="Validation Override",
    description=(
        "Demonstrates how to override FastAPI's default validation error "
        "response with a custom JSON format."
    ),
    version="1.0.0",
)

class Item(BaseModel):
    name: str
    price: float



@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    """
    Convert FastAPI's default validation errors into a custom response format.

    By default, FastAPI returns:
    - HTTP 422 Unprocessable Entity
    - a structured validation payload defined by the framework

    In this example, we override that behavior and return:
    - HTTP 400 Bad Request
    - a custom JSON object with:
        * error: a machine-friendly top-level error category
        * issues: a simplified list of field-level problems

    Why do this?
    - to keep error responses consistent across your API
    - to simplify client-side parsing
    - to match an existing API contract

    Notes:
    - `request` is available if you want to log request metadata.
    - `exc.errors()` returns detailed validation entries produced by FastAPI/Pydantic.
    """
    return JSONResponse(
        status_code=400,
        content={
            "error": "invalid_request",
            "issues": [
                {
                    # `loc` is typically something like:
                    # ("path", "item_id") or ("query", "limit")
                    # We skip the first part ("path"/"query"/"body")
                    # and join the rest into a field name.
                    "source": e["loc"][0],
                    "field": ".".join(map(str, e["loc"][1:])),
                    "msg": e["msg"],
                }
                for e in exc.errors()
            ],
        },
    )


@app.get(
    "/items/{item_id}",
    summary="Get an item by integer ID",
    description=(
        "Expects `item_id` to be an integer path parameter. If validation "
        "fails, the custom RequestValidationError handler returns a 400 "
        "response instead of FastAPI's default 422."
    ),
    tags=["Items"],
)
def get_item(item_id: int):
    """
    Return a validated integer item ID.

    Because `item_id` is annotated as `int`, FastAPI attempts to:
    1. read it from the URL path,
    2. convert it from string to int,
    3. reject it if conversion fails.

    Example:
        /items/123   -> valid
        /items/abc   -> invalid, handled by the custom validation handler
    """
    return {"item_id": item_id}

@app.post(
    "/items",
    summary="Create a new item with validation",
    description=(
        "Accepts an item as a JSON body. If validation fails, the custom "
        "RequestValidationError handler returns a 400 response instead of "
        "FastAPI's default 422."
    ),
    tags=["Items"],
)
def create_item(item: Item, q: int = 1):
    """
    Create a new item.

    Example:
        POST /items
        {
            "name": "Apple",
            "price": 1.23
        }
        -> {"name": "Apple", "price": 1.23}
    """
    return item