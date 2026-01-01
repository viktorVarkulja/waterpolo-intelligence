from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

security = HTTPBearer()


def create_access_token(username: str, expires_minutes: int = 60) -> str:
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(minutes=expires_minutes),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.admin_jwt_secret, algorithm="HS256")


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.admin_jwt_secret, algorithms=["HS256"])
        return payload.get("sub", "")
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc


def verify_login(username: str, password: str) -> bool:
    return username == settings.admin_username and password == settings.admin_password
