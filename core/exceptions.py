from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
    status_code: int = 400
    error_code: str = "APP_ERROR"
    def __init__(self, message: str, *, status_code: int | None = None, error_code: str | None = None, context: dict | None = None):
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        if error_code is not None:
            self.error_code = error_code
        self.context = context or {}


class ExpenseNotFound(AppError):
    status_code = 404
    error_code = "EXPENSE_NOT_FOUND"


async def app_error_handler(request: Request, exc: AppError):
    payload = {
        "ok": False,
        "status": exc.status_code,
        "error": exc.error_code,
        "message": exc.message,
        "path": str(request.url.path),
    }
    if getattr(exc, "context", None):
        payload["context"] = exc.context
    return JSONResponse(status_code=exc.status_code, content=payload)


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    error_code = "HTTP_NOT_FOUND" if exc.status_code == 404 else "HTTP_ERROR"
    payload = {
        "ok": False,
        "status": exc.status_code,
        "error": error_code,
        "message": str(exc.detail),
        "path": str(request.url.path),
    }
    return JSONResponse(status_code=exc.status_code, content=payload)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    payload = {
        "ok": False,
        "status": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "error": "VALIDATION_ERROR",
        "message": "There was a problem with your request payload.",
        "path": str(request.url.path),
        "details": exc.errors(),
    }
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=payload)
