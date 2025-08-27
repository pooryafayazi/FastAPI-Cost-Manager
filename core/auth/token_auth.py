# core/auth/basic_auth.py
from fastapi import Depends, HTTPException, status
from users.models import TokenModel
from core.db import get_db
from sqlalchemy.orm import Session
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


security = HTTPBearer()


def get_authenticated_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token_obj = db.query(TokenModel).filter_by(token=credentials.credentials).one_or_none()
    if not token_obj:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    return token_obj.users
