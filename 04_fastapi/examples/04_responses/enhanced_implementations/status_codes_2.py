"""
04 — Responses: Custom Status Codes

This example demonstrates how to return more appropriate HTTP status codes
for different API operations.

Covered concepts:
1. 201 Created
   Used when a new resource is successfully created.

2. 204 No Content
   Used when an operation succeeds but no response body is returned.

3. status module
   FastAPI provides named constants for HTTP status codes through
   `fastapi.status`, which improves readability over raw integers.

Run:
    uvicorn examples.04_responses.status_codes:app --reload

Alternative:
    fastapi dev status_codes.py

Open API docs:
    http://localhost:8000/docs

Try in /docs:
    POST /items
    with body:
    {
        "name": "Mug",
        "price": 8.5
    }
    -> 201 Created

    DELETE /items/1
    -> 204 No Content
"""

from fastapi import FastAPI, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="Status Codes",
    description=(
        "Demonstrates custom HTTP status codes for create and delete operations."
    ),
    version="1.0.0",
)


class Item(BaseModel):
    """
    Request/response model representing an item.

    Fields:
    - name: item name
    - price: item price
    """
    name: str = Field(..., description="The name of the item", examples=["Mug"])
    price: float = Field(..., description="The price of the item", examples=[8.5])


# Store demo state on the FastAPI app instance
app.state.items_db: dict[int, Item] = {}
app.state.counter = 0


@app.post(
    "/items",
    response_model=Item,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new item",
    description=(
        "Creates a new item and returns it with HTTP 201 Created. "
        "This status code indicates that a new resource was successfully created."
    ),
    tags=["Items"],
)
def create_item(item: Item):
    """
    Create a new item and return it.

    Why 201?
    `201 Created` is the conventional HTTP status code for successful
    resource creation.

    In this demo:
    - the item is stored in an in-memory dictionary
    - a numeric ID is generated internally
    - the created item is returned in the response body

    Note:
    The generated ID is not returned here because the response model is `Item`.
    A more realistic API would usually return the ID as well.
    """
    app.state.counter += 1
    app.state.items_db[app.state.counter] = item
    return item


@app.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an item",
    description=(
        "Deletes an item by ID and returns HTTP 204 No Content. "
        "This means the operation succeeded and no response body is returned."
    ),
    tags=["Items"],
)
def delete_item(item_id: int):
    """
    Delete an item by ID.

    Why 204?
    `204 No Content` is commonly used when a delete operation succeeds
    and there is nothing meaningful to send back in the response body.

    Important detail:
    A 204 response must not include a response body.

    In this example:
    - if the item exists, it is removed
    - if the item does not exist, `pop(..., None)` avoids raising an error

    For teaching simplicity, missing items are ignored here.
    In a production API, you might prefer returning 404 Not Found.
    """
    app.state.items_db.pop(item_id, None)