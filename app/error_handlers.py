"""
Central place for mapping domain exceptions (app/exceptions.py) to HTTP
responses, plus one handler for FastAPI/Pydantic's own automatic
validation errors. Kept separate from main.py so that adding a new error
type later doesn't mean growing the app entrypoint — just add one handler
here.
"""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.exceptions import BadRequestError, ConflictError, NotFoundError, UnprocessableError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(status_code=400, content={"detail": exc.errors()})

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return JSONResponse(status_code=404, content={"detail": exc.detail})

    @app.exception_handler(UnprocessableError)
    async def unprocessable_handler(request: Request, exc: UnprocessableError):
        return JSONResponse(status_code=422, content={"detail": exc.detail})

    @app.exception_handler(ConflictError)
    async def conflict_handler(request: Request, exc: ConflictError):
        return JSONResponse(status_code=409, content=exc.body)
