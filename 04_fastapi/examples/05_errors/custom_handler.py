"""
05 — Error Handling: Custom Exception Handler

Run:  uvicorn examples.05_errors.custom_handler:app --reload

Try in /docs:
  POST /orders?n=0 → custom JSON error
  POST /orders?n=5 → 200 OK
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="Custom Exception Handler")


# Step 1: Define a custom exception class
class BusinessError(Exception):
    """A business-logic error with a code and message."""
    def __init__(self, code: str, msg: str):
        self.code = code
        self.msg = msg


# Step 2: Register a handler for it
# What does it mean to register a handler?
# "If anywhere in the application a BusinessError occurs, then execute this function."
@app.exception_handler(BusinessError)
async def business_error_handler(request: Request, exc: BusinessError):
    """Turn any BusinessError into a tidy JSON response."""
    return JSONResponse(
        status_code=422,
        content={"code": exc.code, "message": exc.msg},
    )


# Step 3: Raise it in your endpoints
@app.post("/orders")
def place_order(n: int):
    """Place an order. Quantity must be positive."""
    if n <= 0:
        raise BusinessError("INVALID_QTY", "Quantity must be positive")
    return {"ok": True, "quantity": n}

'''
custom_handler.py
"Φτιάχνω δική μου exception και αποφασίζω πώς θα φαίνεται στον client"

validation_override.py
"Αλλάζω τη μορφή των error που ήδη στέλνει αυτόματα το FastAPI για λάθος input"
'''