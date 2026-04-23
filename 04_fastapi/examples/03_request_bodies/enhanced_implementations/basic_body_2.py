"""
03 — Request Bodies: Pydantic Model Basics

This example introduces one of the most important FastAPI features:
using Pydantic models to validate JSON request bodies.

Covered concepts:
1. Request body parsing
   If a function parameter is a Pydantic model, FastAPI reads it from the JSON body.

2. Validation
   FastAPI validates the incoming JSON according to the model fields and types.

3. Default values
   Model fields can define defaults, making them optional in the incoming JSON.

4. model_dump()
   Pydantic models can be converted to normal Python dictionaries.

Run:
    uvicorn examples.03_request_bodies.basic_body:app --reload

Alternative:
    fastapi dev basic_body.py

Open API docs:
    http://localhost:8000/docs

Try in /docs:
    POST /items
    with body:
    {
        "name": "Mug",
        "price": 8.5
    }
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field

# Create the FastAPI application instance.
# Its metadata is displayed in the Swagger/OpenAPI documentation.
app = FastAPI(
    title="Request Bodies — Basics",
    description=(
        "Demonstrates how FastAPI uses Pydantic models to validate "
        "JSON request bodies."
    ),
    version="1.0.0",
)


class Item(BaseModel):
    """
    Pydantic model representing an item sent in the request body.

    Fields:
    - name: required string
    - price: required float
    - in_stock: optional boolean with a default value
    - tags: optional list of strings with a default empty list

    FastAPI uses this model to:
    - parse the incoming JSON body,
    - validate field types,
    - generate API documentation automatically.
    """
    name: str = Field(..., description="The name of the item", examples=["Mug"])
    price: float = Field(..., description="The price of the item", examples=[8.5])
    in_stock: bool = Field(
        default=True,
        description="Whether the item is currently available in stock",
        examples=[True],
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Optional list of tags associated with the item",
        examples=[["kitchen", "ceramic"]],
    )


@app.post(
    "/items",
    summary="Create a new item from a JSON request body",
    description=(
        "Accepts a JSON body matching the Item model. FastAPI validates "
        "the payload automatically and returns 422 if the body is invalid."
    ),
    tags=["Items"],
)
def create_item(item: Item):
    """
    Create an item from the request body.

    Because `item` is a Pydantic model, FastAPI reads it from the JSON body.

    This means FastAPI will:
    1. parse the incoming JSON,
    2. validate that the required fields exist,
    3. validate that their types are correct,
    4. apply default values for omitted optional fields,
    5. return a 422 response if validation fails.

    Example valid body:
        {
            "name": "Mug",
            "price": 8.5
        }

    Example invalid body:
        {
            "name": "Mug",
            "price": "cheap"
        }
    """
    return {
        "ok": True,
        "item": item.model_dump(),
        "types": {
            "name": type(item.name).__name__,
            "price": type(item.price).__name__,
            "in_stock": type(item.in_stock).__name__,
            "tags": type(item.tags).__name__,
        },
    }


@app.get(
    "/demo",
    summary="Show how model_dump() works",
    description=(
        "Creates a sample Item instance and returns the result of "
        "calling model_dump(), which converts the model into a plain dictionary."
    ),
    tags=["Demo"],
)
def demo():
    """
    Demonstrate how a Pydantic model becomes a normal Python dictionary.

    `model_dump()` is useful when:
    - you want a plain dict representation,
    - you want to serialize data manually,
    - you want to inspect validated model contents.

    Note:
    The returned value is a standard dictionary, not a Pydantic model object.
    """
    item = Item(name="Book", price=19.99)
    return item.model_dump()
    # Result:
    # {
    #     "name": "Book",
    #     "price": 19.99,
    #     "in_stock": True,
    #     "tags": []
    # }