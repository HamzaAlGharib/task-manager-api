import os

import jwt
from pwdlib import PasswordHash
from dotenv import load_dotenv
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

load_dotenv()

security = HTTPBearer()
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_access_token(user_id: int) -> str:
    secret_key = os.getenv("JWT_SECRET_KEY")

    payload = {"sub": str(user_id)}

    return jwt.encode(payload, secret_key, algorithm="HS256")


def get_current_user( credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    secret_key = os.getenv("JWT_SECRET_KEY")

    try:
        token = credentials.credentials
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=401, detail="Invalid authentication credentials"
            )

        return int(user_id)

    except (jwt.InvalidTokenError, ValueError):
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )
