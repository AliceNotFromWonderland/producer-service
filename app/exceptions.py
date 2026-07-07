"""
Domain-level exceptions.

Each one maps to a specific HTTP status code via the handlers registered in
app/error_handlers.py. Services raise these instead of HTTPException
directly, keeping the services layer framework-agnostic.
"""


class AppError(Exception):
    """Base class for all domain errors."""


class BadRequestError(AppError):
    """Maps to HTTP 400 — malformed input / missing required fields."""

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class NotFoundError(AppError):
    """Maps to HTTP 404 — referenced entity does not exist."""

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class UnprocessableError(AppError):
    """Maps to HTTP 422 — semantically invalid input (business rule violation)."""

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class ConflictError(AppError):
    """
    Maps to HTTP 409.

    `body` is used as-is as the JSON response body, so callers can shape it
    per-endpoint, e.g. {"detail": "..."} or
    {"error": "insufficient stock", "available_quantity": 3}.
    """

    def __init__(self, body: dict):
        self.body = body
        super().__init__(str(body))
