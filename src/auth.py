import os

import jwt
from pwdlib import PasswordHash
from dotenv import load_dotenv
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta, timezone
import uuid

load_dotenv()

security = HTTPBearer()
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_access_token(user_id: int) -> str:
    secret_key = os.getenv("JWT_SECRET_KEY")

    expiration = datetime.now(timezone.utc) + timedelta(minutes=30)

    payload = {"sub": str(user_id), "type": "access", "exp": expiration}

    return jwt.encode(payload, secret_key, algorithm="HS256")


def create_refresh_token(user_id: int) -> tuple[str, str]:
    secret_key = os.getenv("JWT_SECRET_KEY")

    jti = str(uuid.uuid4())

    expiration = datetime.now(timezone.utc) + timedelta(days=7)

    payload = {"sub": str(user_id), "type": "refresh", "jti": jti, "exp": expiration}

    token = jwt.encode(payload, secret_key, algorithm="HS256")

    return token, jti


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    secret_key = os.getenv("JWT_SECRET_KEY")

    try:
        token = credentials.credentials
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])

        user_id = payload.get("sub")
        token_type = payload.get("type")

        if token_type != "access":
            raise HTTPException(
                status_code=401, detail="Invalid authentication credentials"
            )

        if user_id is None:
            raise HTTPException(
                status_code=401, detail="Invalid authentication credentials"
            )

        return int(user_id)

    except (jwt.InvalidTokenError, ValueError):
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )
