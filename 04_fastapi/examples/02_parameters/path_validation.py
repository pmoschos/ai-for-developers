"""
02 — Path Parameters: Validation with Path(...)

This example shows how to add validation rules and documentation metadata
to a FastAPI path parameter using Path(...).

Why use Path(...)?
- It lets you enforce numeric constraints such as minimum/maximum values.
- It enriches the generated API docs with descriptions and examples.
- It keeps validation close to the parameter definition.

Run:
    uvicorn examples.02_parameters.path_validation:app --reload

Alternative:
    fastapi dev path_validation.py

Open API docs:
    http://localhost:8000/docs

Try:
    GET /items/5
        -> 200 OK

    GET /items/0
        -> 422 Unprocessable Entity (fails ge=1)

    GET /items/99999
        -> 422 Unprocessable Entity (fails le=10000)
"""

# To run this code:
# fastapi dev path_validation.py
# or
# uvicorn path_validation:app --reload
# To view the Swagger UI documentation:
# http://localhost:8000/docs

from typing import Annotated

from fastapi import FastAPI, Path

# Create the FastAPI application instance.
# The metadata below is displayed in the generated Swagger/OpenAPI docs.
app = FastAPI(
    title="Path Validation",
    description=(
        "Demonstrates validation and documentation metadata for path "
        "parameters using FastAPI's Path(...)."
    ),
    version="1.0.0",
)


@app.get("/items/{item_id}",
    summary="Get an item by validated ID",
    description=(
        "Accepts an integer item ID from the URL path and validates it "
        "using Path(...). The value must be between 1 and 10,000 inclusive."
    ),
    tags=["Items"])
def get_item(
    item_id: Annotated[int, Path(
        ge=1,
        le=10_000,
        description="The ID of the item to retrieve",
        examples=[42],
    )]
):
    """
    Return an item identifier after validation.

    `Path(...)` adds both validation rules and API documentation metadata.

    In this example:
    - `ge=1` means the value must be greater than or equal to 1
    - `le=10_000` means the value must be less than or equal to 10,000
    - `description` appears in the generated docs
    - `examples` helps document valid sample input

    FastAPI uses both:
    - the Python type hint (`int`) for type validation/conversion
    - the `Path(...)` metadata for extra constraints and docs

    Example:
        /items/5       -> valid
        /items/0       -> invalid (too small)
        /items/99999   -> invalid (too large)
    """
    return {
        "item_id": item_id,
        "kind": type(item_id).__name__,  # confirms the value is an int
    }
