# core/auth/jwt_auth.py
from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import DecodeError, InvalidSignatureError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from core.config import settings
from core.db import get_db
from users.models import UserModel

from i18n.utils import _


security = HTTPBearer()


def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):

    token = credentials.credentials
    try:
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        user_id = decoded.get("user_id", None)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                # detail="Authentication failed, user_id not in the payload",
                detail=_("Authentication failed: user_id missing in token payload."),
            )

        if decoded.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                # detail="Authentication failed, token type not valid",
                detail=_("Authentication failed: token type is not valid."),
            )

        if datetime.now() > datetime.fromtimestamp(decoded.get("exp", 0)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                # detail="Authentication failed, token expired",
                detail=_("Authentication failed: token has expired."),
            )

        user_obj = db.query(UserModel).filter_by(id=user_id).one()
        return user_obj

    except InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            # detail="Authenticated failed, Invalid Signature",
            detail=_("Authentication failed: invalid signature."),
        )
    except DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            # detail="Authenticated failed, Decode failed",
            detail=_("Authentication failed: decode failed."),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            # detail=f"Authenticated failed, {e}",
            detail=_("Authentication failed: {error}").format(error=str(e)),
        )


def generate_access_token(user_id: int, expires_in: int = 60 * 5) -> str:

    now = datetime.now(timezone.utc)
    payload = {
        "type": "access",
        "user_id": user_id,
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


def generate_refresh_token(user_id: int, expires_in: int = 7 * 24 * 3600) -> str:

    now = datetime.now(timezone.utc)
    payload = {
        "type": "refresh",
        "user_id": user_id,
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


def decode_refresh_token(token):

    try:
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        user_id = decoded.get("user_id", None)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                # detail="Authentication failed, user_id not in the payload",
                detail=_("Authentication failed: user_id missing in token payload."),
            )
        if decoded.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                # detail="Authentication failed, token type not valid",
                detail=_("Authentication failed: token type is not valid."),
            )
        if datetime.now() > datetime.fromtimestamp(decoded.get("exp", 0)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                # detail="Authentication failed, token expired",
                detail=_("Authentication failed: token has expired."),
            )

        return user_id

    except InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            # detail="Authenticated failed, Invalid Signature",
            detail=_("Authentication failed: invalid signature."),
        )
    except DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            # detail="Authenticated failed, Decode failed",
             detail=_("Authentication failed: decode failed."),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            # detail=f"Authenticated failed, {e}",
            detail=_("Authentication failed: {error}").format(error=str(e)),
        )
