"""
04 — Responses: Custom Status Codes

Run:  uvicorn examples.04_responses.status_codes:app --reload

Try in /docs:
  POST /items → 201 Created
  DELETE /items/1 → 204 No Content
"""

from fastapi import FastAPI, status
from pydantic import BaseModel

app = FastAPI(title="Status Codes")


class Item(BaseModel):
    name: str
    price: float


items_db: dict[int, Item] = {}
counter = 0


@app.post(
    "/items",
    response_model=Item,
    status_code=status.HTTP_201_CREATED,
)
def create_item(item: Item):
    """Use status.HTTP_201_CREATED for new resources."""
    global counter
    counter += 1
    items_db[counter] = item
    return item


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int):
    """204 No Content — successful deletion with no response body."""
    items_db.pop(item_id, None)
