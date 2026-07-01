

from datetime import datetime, timedelta, timezone

import jwt

from fastapi import status
from app.core.config import settings
from app.core.exceptions import ApiException


ALGORITHM = "HS256"
SECRETE_JWT_KEY=settings.SECRETE_JWT_KEY
ACCESS_TOKEN_EXPIRE_DAYS = 30


if not SECRETE_JWT_KEY:
    raise ApiException("secrete key not found in .env")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRETE_JWT_KEY, algorithm=ALGORITHM)



def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRETE_JWT_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ApiException("Token has expired", status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError:
        raise ApiException("Invalid token", status.HTTP_401_UNAUTHORIZED)

