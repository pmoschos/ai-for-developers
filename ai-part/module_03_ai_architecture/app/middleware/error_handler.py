"""
Error Handler Middleware
========================
Centralized error handling for the API.
"""

import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from openai import APIError, RateLimitError, APIConnectionError, APITimeoutError

from app.models import ErrorResponse

logger = logging.getLogger(__name__)


def setup_error_handlers(app: FastAPI):
    """Configure error handlers for the FastAPI application"""
    
    @app.exception_handler(RateLimitError)
    async def rate_limit_handler(request: Request, exc: RateLimitError):
        """Handle OpenAI rate limit errors"""
        logger.warning(f"Rate limit exceeded: {exc}")
        return JSONResponse(
            status_code=429,
            content=ErrorResponse(
                error="rate_limit_exceeded",
                message="API rate limit exceeded. Please try again later.",
                details={"retry_after": 60}
            ).model_dump()
        )
    
    @app.exception_handler(APITimeoutError)
    async def timeout_handler(request: Request, exc: APITimeoutError):
        """Handle API timeout errors"""
        logger.error(f"API timeout: {exc}")
        return JSONResponse(
            status_code=504,
            content=ErrorResponse(
                error="timeout",
                message="The AI service took too long to respond. Please try again.",
                details=None
            ).model_dump()
        )
    
    @app.exception_handler(APIConnectionError)
    async def connection_handler(request: Request, exc: APIConnectionError):
        """Handle connection errors"""
        logger.error(f"Connection error: {exc}")
        return JSONResponse(
            status_code=503,
            content=ErrorResponse(
                error="connection_error",
                message="Unable to connect to AI service. Please try again.",
                details=None
            ).model_dump()
        )
    
    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, exc: APIError):
        """Handle general API errors"""
        logger.error(f"API error: {exc}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="api_error",
                message="An error occurred with the AI service.",
                details={"message": str(exc)}
            ).model_dump()
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions"""
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error="http_error",
                message=exc.detail,
                details=None
            ).model_dump()
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions"""
        logger.exception(f"Unexpected error: {exc}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="internal_error",
                message="An unexpected error occurred.",
                details=None
            ).model_dump()
        )
