"""
05 — Error Handling: Override Validation Errors

Run:  uvicorn examples.05_errors.validation_override:app --reload

Try:
  GET /items/abc → custom 400 error instead of default 422
"""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI(title="Validation Override")


@app.exception_handler(RequestValidationError)
async def validation_handler(request, exc: RequestValidationError):
    """
    Override Pydantic's default 422 response with your own shape.
    This gives you control over the error format sent to clients.
    """
    return JSONResponse(
        status_code=400,
        content={
            "error": "invalid_request",
            "issues": [
                {
                    "field": ".".join(map(str, e["loc"][1:])),
                    "msg": e["msg"],
                }
                for e in exc.errors()
            ],
        },
    )
#e["loc"] = ("path", "item_id")
#               ↑          ↑
#             source    parameter name

# map(str, ("items", 0, "name"))  →  ["items", "0", "name"]
# ".".join(["item_id"])             →  "item_id"
# ".".join(["address", "zip_code"]) →  "address.zip_code"
# ".".join(["items", "0", "name"])  →  "items.0.name"


@app.get("/items/{item_id}")
def get_item(item_id: int):
    """Try GET /items/abc to see the custom validation error format."""
    return {"item_id": item_id}


