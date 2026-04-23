"""
03 — Request Bodies: Nested Models

Run:  uvicorn examples.03_request_bodies.nested_models:app --reload

Try in /docs:
  POST /customers with nested shipping address
"""

from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

app = FastAPI(title="Nested Models")


class Address(BaseModel):
    street: str
    city: str
    country: str = "GR"


class Customer(BaseModel):
    """Compose models. FastAPI validates nested structures recursively."""
    name: str
    email: EmailStr
    shipping: Address                    # required nested model
    billing: Address | None = None       # optional nested model


@app.post("/customers")
def create_customer(customer: Customer):
    """
    Send a JSON body like:
    {
        "name": "Alice",
        "email": "alice@example.com",
        "shipping": {"street": "123 Main St", "city": "Athens"},
        "billing": null
    }
    """
    return customer
