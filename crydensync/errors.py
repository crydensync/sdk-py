"""Errors returned by the CrydenSync API and SDK transport."""

from typing import Optional


class CrydenError(Exception):
    """An API or network error with a stable code and HTTP status."""

    def __init__(self, code: str, message: str, status: int) -> None:
        super().__init__(message)
        self.code = code
        self.status = status


def error_from_payload(status: int, payload: object) -> CrydenError:
    error: Optional[dict] = None
    if isinstance(payload, dict) and isinstance(payload.get("error"), dict):
        error = payload["error"]
    code = error.get("code", "internal_error") if error else "internal_error"
    message = error.get("message", "an unexpected error occurred") if error else "an unexpected error occurred"
    return CrydenError(str(code), str(message), status)
