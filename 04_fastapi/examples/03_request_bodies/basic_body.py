from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Request Bodies — Basics")

# To run this code:
# fastapi dev basic_body.py
# or
# uvicorn basic_body:app --reload
# To view the Swagger UI documentation:
# http://localhost:8000/docs

class Item(BaseModel):
    """A Pydantic model that validates incoming JSON."""
    name: str
    price: float
    in_stock: bool = True
    tags: list[str] = Field(default_factory=list)


items: list[Item] = []


@app.post("/items")
def create_item(item: Item):
    """
    Any Pydantic model used as an argument is read from the JSON body.
    FastAPI validates the data and returns 422 if it's invalid.
    """
    items.append(item)
    return {"ok": True, "item": item}


@app.get("/items")
def get_items():
    """Return all items."""
    return {"items": items}


@app.get("/demo")
def demo():
    """Show how model_dump() converts a model to a dictionary."""
    item = Item(name="Book", price=19.99)
    return item.model_dump()