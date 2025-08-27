# core/auth/jwt_cookie_auth.py
from datetime import datetime, timezone
from hmac import compare_digest
import secrets
import jwt
from fastapi import Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from i18n.i18n import I18n, get_translator
from core.config import settings
from core.db import get_db
from users.models import UserModel


CSRF_COOKIE_NAME = "csrf_token"


def set_csrf_cookie(response: Response) -> str:
    token = secrets.token_urlsafe(32)
    # Intentionally HttpOnly=False so that JS can send it in the header (double-submit pattern)
    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=token,
        max_age=settings.REFRESH_MAX_AGE,
        httponly=False,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        domain=settings.COOKIE_DOMAIN,
        path="/",
    )
    return token


def verify_csrf(request: Request, tr: I18n = Depends(get_translator)) -> None:
    header = request.headers.get("x-csrf-token")
    cookie = request.cookies.get(CSRF_COOKIE_NAME)
    if not header or not cookie or compare_digest(header, cookie):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=tr("common.forbidden_csrf")
        )


def _decode_and_validate(
    token: str, expected_type: str, tr: I18n = Depends(get_translator)
) -> dict:
    # decode & validation (type & exp) JWT
    try:
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=tr("auth.token_expired"),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=tr("auth.invalid_token"),
            headers={"WWW-Authenticate": "Bearer"},
        )

    if decoded.get("type") != expected_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=tr("auth.invalid_token_type"),
            headers={"WWW-Authenticate": "Bearer"},
        )

    exp = decoded.get("exp")
    if exp is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=tr("auth.invalid_token_payload"),
            headers={"WWW-Authenticate": "Bearer"},
        )

    # compare TZ-aware
    if datetime.now(timezone.utc) > datetime.fromtimestamp(exp, tz=timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=tr("auth.token_expired"),
            headers={"WWW-Authenticate": "Bearer"},
        )

    return decoded


def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    # set both cookies (scure & HttpOnly)
    response.set_cookie(
        key=settings.COOKIE_ACCESS_NAME,
        value=access_token,
        max_age=settings.ACCESS_MAX_AGE,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        domain=settings.COOKIE_DOMAIN,
        path="/",
    )

    response.set_cookie(
        key=settings.COOKIE_REFRESH_NAME,
        value=refresh_token,
        max_age=settings.REFRESH_MAX_AGE,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        domain=settings.COOKIE_DOMAIN,
        path="/",
    )


def set_access_cookie(response: Response, access_token: str) -> None:
    # update cookie access
    response.set_cookie(
        key=settings.COOKIE_ACCESS_NAME,
        value=access_token,
        max_age=settings.ACCESS_MAX_AGE,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        domain=settings.COOKIE_DOMAIN,
        path="/",
    )


def clear_auth_cookies(response: Response) -> None:
    # clear cookies (logout)
    response.delete_cookie(settings.COOKIE_ACCESS_NAME, path="/")
    response.delete_cookie(settings.COOKIE_REFRESH_NAME, path="/")


def get_current_user_from_cookies(
    request: Request,
    db: Session = Depends(get_db),
    tr: I18n = Depends(get_translator),
) -> UserModel:
    # Dependency reads the access cookie for protected routes
    token = request.cookies.get(settings.COOKIE_ACCESS_NAME)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=tr("auth.missing_access_cookie"),
            headers={"WWW-Authenticate": "Bearer"},
        )

    decoded = _decode_and_validate(token, expected_type="access")
    user_id = decoded.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=tr("auth.invalid_token_payload"),
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(UserModel).filter(UserModel.id == user_id).one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=tr("auth.user_not_found"),
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_user_id_from_refresh_cookie(
    request: Request, tr: I18n = Depends(get_translator)
) -> int:
    # For refresh: Returns only the user_id from the refresh token in the cookie.
    token = request.cookies.get(settings.COOKIE_REFRESH_NAME)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=tr("auth.missing_refresh_cookie"),
            headers={"WWW-Authenticate": "Bearer"},
        )

    decoded = _decode_and_validate(token, expected_type="refresh")
    user_id = decoded.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=tr("auth.invalid_token_payload"),
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id
