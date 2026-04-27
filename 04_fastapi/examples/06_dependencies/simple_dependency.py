"""
06 — Dependencies: Simple Function Dependency

Run:  uvicorn examples.06_dependencies.simple_dependency:app --reload

Try:
  GET /items?skip=10&limit=5
  GET /users?limit=3
"""

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException

app = FastAPI(title="Simple Dependencies")

fake_items = [{"name": f"Item {i}"} for i in range(100)]
fake_users = [{"name": f"User {i}"} for i in range(50)]


# Without the dependency (the problem)
'''
@app.get("/items")
def list_items(skip: int = 0, limit: int = 10):
    """
    Returns items with pagination, but without using a dependency.
    """
    return fake_items[skip : skip + limit]


@app.get("/users")
def list_users(skip: int = 0, limit: int = 10):   # ← copy-paste
    """
    Returns users with pagination, but without using a dependency.
    """
    return fake_users[skip : skip + limit]


@app.get("/products")
def list_products(skip: int = 0, limit: int = 10):  # ← again...
    """
    Returns products with pagination, but without using a dependency.
    """
    return fake_products[skip : skip + limit]
'''


def pagination(skip: int = 0, limit: int = 10):
    """A reusable dependency that extracts pagination parameters."""
    return {"skip": skip, "limit": limit} # ← this is a dict, as we defined it


# Create a type alias for cleaner signatures
# dict as defined above (pagination function returns a dict)
Page = Annotated[dict, Depends(pagination)] 

'''
# If it returned a tuple → you'd use tuple
def pagination(...):
    return (skip, limit)

Page = Annotated[tuple, Depends(pagination)]

# If it returned a Pydantic model → you'd use that class
class PageParams(BaseModel):
    skip: int
    limit: int

def pagination(...):
    return PageParams(skip=skip, limit=limit)
    
Page = Annotated[PageParams, Depends(pagination)]
'''


@app.get("/items")
def list_items(page: Page):
    """Both endpoints share the same pagination logic."""
    return fake_items[page["skip"]: page["skip"] + page["limit"]]


@app.get("/users")
def list_users(page: Page):
    """Reuse the same Page dependency — no code duplication."""
    return fake_users[page["skip"]: page["skip"] + page["limit"]]


fake_products = [
    {"name": f"Product {i}", "category": "electronics" if i % 2 == 0 else "clothing"}
    for i in range(80)
]


@app.get("/products")
def list_products(page: Page, category: str | None = None):
    """Dependency + own parameter: pagination is reused, category is endpoint-specific.
    /products?category=electronics
    /products?category=clothing&skip=10&limit=5
    """
    results = fake_products
    if category:
        results = [p for p in results if p["category"] == category]
    return results[page["skip"]: page["skip"] + page["limit"]]


@app.get("/search/{collection}")
def search(collection: str, page: Page, q: str):
    """Search a collection by name, with pagination.
    /search/items?q=Item 5
    /search/users?q=User&skip=0&limit=3
    /search/products?q=Product&skip=10&limit=5
    """
    collections = {
        "items": fake_items,
        "users": fake_users,
        "products": fake_products,
    }
    if collection not in collections:
        raise HTTPException(status_code=404, detail=f"Unknown collection '{collection}'")
    matches = [d for d in collections[collection] if q.lower() in d["name"].lower()]

    return matches[page["skip"]: page["skip"] + page["limit"]]
