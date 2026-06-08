from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.contracts.error_contract import ErrorDetailContract, ErrorResponseContract


class AppException(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = "internal_error"

    def __init__(
        self,
        message: str = "An unexpected application error occurred.",
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.details = details
        super().__init__(message)


class ResourceNotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "resource_not_found"


class ServiceUnavailableError(AppException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error_code = "service_unavailable"


class InvalidRequestError(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "invalid_request"


def build_error_response(
    *,
    status_code: int,
    error_code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    payload = ErrorResponseContract(
        error=ErrorDetailContract(
            code=error_code,
            message=message,
            details=details,
        )
    )
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(payload),
    )


async def app_exception_handler(
    request: Request,
    exc: AppException,
) -> JSONResponse:
    return build_error_response(
        status_code=exc.status_code,
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    return build_error_response(
        status_code=exc.status_code,
        error_code="http_error",
        message=str(exc.detail),
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return build_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_code="validation_error",
        message="Request validation failed.",
        details={"errors": exc.errors()},
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    return build_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code="internal_error",
        message="An unexpected server error occurred.",
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
