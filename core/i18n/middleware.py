# core/i18n/middleware.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from i18n.utils import set_locale_from_header

class LanguageMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        set_locale_from_header(request.headers.get("Accept-Language"))
        response = await call_next(request)
        return response
