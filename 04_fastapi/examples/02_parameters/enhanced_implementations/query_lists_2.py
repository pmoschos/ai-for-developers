from typing import Annotated

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI(title="Query Lists & Booleans")


class ProductFilterResponse(BaseModel):
    tags: list[str] | None = Field(
        default=None,
        description="The list of provided product tags, or None if omitted.",
    )
    min_price: float = Field(
        ...,
        description="The validated minimum price filter.",
    )
    on_sale: bool = Field(
        ...,
        description="Whether the on-sale filter is enabled.",
    )


@app.get("/products", response_model=ProductFilterResponse, tags=["Products"])
def products(
    tags: Annotated[list[str] | None, Query()] = None,
    min_price: float = 0,
    on_sale: bool = False,
):
    """
    Demonstrate list and boolean query parameter parsing.
    """
    return ProductFilterResponse(
        tags=tags,
        min_price=min_price,
        on_sale=on_sale,
    )