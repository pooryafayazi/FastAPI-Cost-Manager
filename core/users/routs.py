# core/users/routs.py
from fastapi import status, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from core.db import get_db
from users.models import UserModel
from fastapi import APIRouter
from users.schemas import UserLoginSchema, UserRegisterSchema
from auth.jwt_auth import generate_access_token, generate_refresh_token
import secrets
from auth.jwt_cookie_auth import (
    set_auth_cookies,
    set_access_cookie,
    clear_auth_cookies,
    get_current_user_from_cookies,
    get_user_id_from_refresh_cookie,
    set_csrf_cookie,
    verify_csrf
)
from fastapi import Request


router = APIRouter(tags=["users"], prefix="/users")


def generate_token(length=32):
    return secrets.token_hex(length)


# ---------- JWT ----------
@router.post("/register")
async def user_register(payload: UserRegisterSchema, db: Session = Depends(get_db)):
    if db.query(UserModel).filter_by(username=payload.username.lower()).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="username already exists!")

    user_obj = UserModel(username=payload.username.lower())
    user_obj.set_password(payload.password)
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    content = {"detail": "user created", "id": user_obj.id, "username": user_obj.username}
    return JSONResponse(content=content)


# ---------- JWT Cookie ----------
@router.post("/login-cookie")
def user_login_cookie(payload: UserLoginSchema, db: Session = Depends(get_db)):
    user_obj = db.query(UserModel).filter_by(username=payload.username.lower()).first()
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username doesnt exists!")
    if not user_obj.verify_password(payload.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="password is invalid!")

    access_token = generate_access_token(user_obj.id)
    refresh_token = generate_refresh_token(user_obj.id)

    # set cookies on response
    resp = JSONResponse(content={"detail": "logged in successfully (cookie auth)"})
    set_auth_cookies(resp, access_token, refresh_token)
    set_csrf_cookie(resp)
    return resp


@router.post("/refresh-cookie")
def user_refresh_cookie(request: Request, x_csrf_token: str = Header(...), _=Depends(verify_csrf)):
    # Reads the refresh token from the cookie, creates a new access token if it is valid, and only updates the access cookie.
    user_id = get_user_id_from_refresh_cookie(request)
    new_access = generate_access_token(user_id)

    resp = JSONResponse(content={"detail": "access token refreshed (cookie auth)"})
    set_access_cookie(resp, new_access)
    return resp


@router.post("/logout-cookie")
def user_logout_cookie(x_csrf_token: str = Header(...), _=Depends(verify_csrf)):
    # clear cookies (logout)
    resp = JSONResponse(content={"detail": "logged out (cookie auth)"})
    clear_auth_cookies(resp)
    return resp


# Example of a cookie-protected rout (instead of Bearer)
@router.get("/me-cookie")
def me_cookie(user: UserModel = Depends(get_current_user_from_cookies)):
    return {"id": user.id, "username": user.username}
