"""
05 — Error Handling: Custom Exception Handler

This example demonstrates how to define and use a custom exception
with a dedicated FastAPI exception handler.

Covered concepts:
1. Custom exception classes
   You can represent business/domain errors with your own exception type.

2. Centralized error handling
   A single exception handler can convert those exceptions into a consistent
   JSON response format.

3. Separation of concerns
   Endpoint logic raises a business error, while the handler decides how the
   HTTP response should look.

4. JSONResponse
   Useful when you want full control over the error payload.

Run:
    uvicorn examples.05_errors.custom_handler:app --reload

Alternative:
    fastapi dev custom_handler.py

Open API docs:
    http://localhost:8000/docs

Try in /docs:
    POST /orders?n=0
        -> custom JSON error

    POST /orders?n=5
        -> 200 OK
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Create the FastAPI application instance.
# Its metadata appears in the generated Swagger/OpenAPI docs.
app = FastAPI(
    title="Custom Exception Handler",
    description=(
        "Demonstrates how to define a custom exception and map it to a "
        "custom JSON error response in FastAPI."
    ),
    version="1.0.0",
)


class BusinessError(Exception):
    """
    Custom exception representing a business-rule violation.

    This is useful when an error is not a framework-level issue
    but a domain/application-level rule violation.

    Fields:
    - code: a machine-friendly error code
    - msg: a human-readable error message
    """

    def __init__(self, code: str, msg: str):
        self.code = code
        self.msg = msg


@app.exception_handler(BusinessError)
async def business_error_handler(request: Request, exc: BusinessError):
    """
    Convert BusinessError into a structured JSON HTTP response.

    Whenever a BusinessError is raised anywhere in the application,
    FastAPI will call this handler automatically.

    Parameters:
    - request: the incoming HTTP request object
    - exc: the raised BusinessError instance

    In this example, the handler returns:
    - HTTP status 422
    - a JSON body with:
        * code
        * message

    The request object is not used directly here, but it can be useful for:
    - logging
    - tracing
    - inspecting headers or request path
    """
    return JSONResponse(
        status_code=422,
        content={
            "code": exc.code,
            "message": exc.msg,
        },
    )


@app.post(
    "/orders",
    summary="Place an order with quantity validation",
    description=(
        "Accepts a quantity as a query parameter. If the quantity is not "
        "positive, a BusinessError is raised and converted to a custom JSON "
        "error response by the registered exception handler."
    ),
    tags=["Orders"],
)
def place_order(n: int):
    """
    Place an order.

    Business rule:
    - quantity must be strictly positive

    If the rule is violated, the endpoint raises `BusinessError`
    instead of manually constructing an HTTP response.

    This keeps the endpoint logic clean:
    - endpoint code focuses on business rules
    - the exception handler focuses on response formatting

    Example success:
        POST /orders?n=5
        -> {"ok": true, "quantity": 5}

    Example failure:
        POST /orders?n=0
        -> 422
        -> {"code": "INVALID_QTY", "message": "Quantity must be positive"}
    """
    if n <= 0:
        raise BusinessError("INVALID_QTY", "Quantity must be positive")

    return {
        "ok": True,
        "quantity": n,
    }