from __future__ import annotations

from app.exceptions import InvalidRequestError, ResourceNotFoundError, ServiceUnavailableError


def not_found(message: str) -> ResourceNotFoundError:
    return ResourceNotFoundError(message)


def bad_request(message: str) -> InvalidRequestError:
    return InvalidRequestError(message)


def service_unavailable(message: str) -> ServiceUnavailableError:
    return ServiceUnavailableError(message)
