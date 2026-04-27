"""
05 — Error Handling: HTTPException

Run:  uvicorn examples.05_errors.http_exception:app --reload

Try:
  GET /items/a → 200 OK ("Apple")
  GET /items/x → 404 Not Found
"""

from fastapi import FastAPI, HTTPException, status

app = FastAPI(title="HTTPException")

items = {"a": "Apple", "b": "Banana", "c": "Cherry"}


@app.get("/items/{key}")
def get_item(key: str):
    """
    Raise HTTPException anywhere — FastAPI turns it into
    a proper HTTP error response with status and message.
    """
    if key not in items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item '{key}' not found",
            headers={"X-Error": "item-missing"},  # optional custom header
        )
    return {"key": key, "name": items[key]}
