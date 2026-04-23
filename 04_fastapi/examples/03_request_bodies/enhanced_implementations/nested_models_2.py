"""
03 — Request Bodies: Nested Models

This example demonstrates how FastAPI and Pydantic handle nested JSON
structures using multiple BaseModel classes.

Covered concepts:
1. Nested request bodies
   A Pydantic model can contain another Pydantic model as a field.

2. Recursive validation
   FastAPI validates nested objects automatically, field by field.

3. Required vs optional nested models
   - `shipping` is required
   - `billing` is optional

4. Default values inside nested models
   The Address model defines a default country value.

Run:
    uvicorn examples.03_request_bodies.nested_models:app --reload

Alternative:
    fastapi dev nested_models.py

Open API docs:
    http://localhost:8000/docs

Try in /docs:
    POST /customers
    with body:
    {
        "name": "Alice",
        "email": "alice@example.com",
        "shipping": {
            "street": "123 Main St",
            "city": "Athens"
        },
        "billing": null
    }
"""

from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, Field

# Create the FastAPI application instance.
# Its metadata appears in the generated Swagger/OpenAPI docs.
app = FastAPI(
    title="Nested Models",
    description=(
        "Demonstrates request body validation using nested Pydantic models."
    ),
    version="1.0.0",
)


class Address(BaseModel):
    """
    Nested model representing a postal address.

    Fields:
    - street: required street name and number
    - city: required city
    - country: optional country code/name with default value 'GR'
    """
    street: str = Field(..., description="Street name and number", examples=["123 Main St"])
    city: str = Field(..., description="City name", examples=["Athens"])
    country: str = Field(
        default="GR",
        description="Country code or country name",
        examples=["GR"],
    )


class Customer(BaseModel):
    """
    Main request model for creating a customer.

    This model demonstrates composition:
    one Pydantic model contains other Pydantic models as fields.

    Fields:
    - name: required customer name
    - email: required valid email address
    - shipping: required nested Address object
    - billing: optional nested Address object
    """
    name: str = Field(..., description="Customer full name", examples=["Alice"])
    email: EmailStr = Field(..., description="Customer email address", examples=["alice@example.com"])
    shipping: Address = Field(..., description="Required shipping address")
    billing: Address | None = Field(
        default=None,
        description="Optional billing address",
    )


@app.post(
    "/customers",
    summary="Create a customer with nested address models",
    description=(
        "Accepts a JSON body containing customer information and nested "
        "address objects. FastAPI validates nested structures recursively."
    ),
    tags=["Customers"],
)
def create_customer(customer: Customer):
    """
    Create a customer from a nested JSON request body.

    Because `customer` is a Pydantic model that contains nested models,
    FastAPI validates the full structure recursively.

    This includes:
    - validating the top-level fields
    - validating the nested `shipping` object
    - validating the nested `billing` object if provided
    - applying default values inside nested models

    Example valid body:
        {
            "name": "Alice",
            "email": "alice@example.com",
            "shipping": {
                "street": "123 Main St",
                "city": "Athens"
            },
            "billing": null
        }

    In the example above:
    - `shipping.country` is omitted
    - Pydantic automatically fills it with "GR"
    """
    return {
        "ok": True,
        "customer": customer.model_dump(),
        "types": {
            "customer": type(customer).__name__,
            "shipping": type(customer.shipping).__name__,
            "billing": type(customer.billing).__name__ if customer.billing is not None else None,
        },
    }