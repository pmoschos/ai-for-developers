"""
03 — Request Bodies: Body + Path + Query Combined

Run:  uvicorn examples.03_request_bodies.body_path_query:app --reload

Try in /docs:
  PUT /items/7?notify=true
  Body: {"name": "Mug", "price": 9.0}
"""

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Body + Path + Query")

# To run this code:
# fastapi dev body_path_query.py
# or
# uvicorn body_path_query:app --reload
# To view the Swagger UI documentation:
# http://localhost:8000/docs

class Item(BaseModel):
    name: str
    price: float
    in_stock: bool = True


@app.put("/items/{item_id}")
def update_item(
    item_id: int,                 # ← path parameter
    item: Item,                   # ← JSON body (Pydantic model)
    notify: bool = False,         # ← query parameter
):
    """
    FastAPI figures out which is which from the declaration:
    - In the URL path → path parameter
    - Pydantic model  → body
    - Everything else  → query parameter
    """
    return {"item_id": item_id, "item": item, "notify": notify}
