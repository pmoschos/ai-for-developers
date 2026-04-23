from typing import Annotated

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI(title="Query Parameters")

fake_items = [{"name": f"Item {i}"} for i in range(100)]


class ItemsResponse(BaseModel):
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Maximum number of items returned")
    count: int = Field(..., description="Number of items in the current response")
    items: list[dict] = Field(..., description="Returned items")


class SearchResponse(BaseModel):
    q: str | None = Field(None, description="Optional validated search query")
    category: str = Field(..., description="Selected category")
    in_stock: bool = Field(..., description="Whether only in-stock items are requested")


@app.get("/items", response_model=ItemsResponse, tags=["Items"])
def list_items(skip: int = 0, limit: int = 10):
    items = fake_items[skip: skip + limit]
    return ItemsResponse(skip=skip, limit=limit, count=len(items), items=items)


@app.get("/search", response_model=SearchResponse, tags=["Search"])
def search(
    q: Annotated[str | None, Query(min_length=3, max_length=50)] = None,
    category: str = "all",
    in_stock: bool = False,
):
    return SearchResponse(q=q, category=category, in_stock=in_stock)