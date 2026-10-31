"""Stable, non-sensitive HTTP error responses."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


async def http_error_handler(
    _request: Request, exception: StarletteHTTPException
) -> JSONResponse:
    return JSONResponse(
        status_code=exception.status_code,
        content={
            "error": {
                "code": "http_error",
                "message": str(exception.detail),
            }
        },
        headers=exception.headers,
    )


async def validation_error_handler(
    _request: Request, _exception: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "invalid_request",
                "message": "Request validation failed.",
            }
        },
    )


def install_error_handlers(app: FastAPI) -> None:
    """Install stable error shapes without returning submitted values."""
    app.add_exception_handler(StarletteHTTPException, http_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
