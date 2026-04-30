"""
Custom Exceptions & Handlers

Defines application-specific exceptions and registers
handlers that convert them into clean JSON responses.
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class BusinessError(Exception):
    """A business-logic error with a machine-readable code and message."""

    def __init__(self, code: str, msg: str):
        self.code = code
        self.msg = msg


def register_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the app instance."""

    @app.exception_handler(BusinessError)
    async def business_error_handler(request: Request, exc: BusinessError):
        return JSONResponse(
            status_code=422,
            content={"code": exc.code, "message": exc.msg},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
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
