import os

import jwt
from pwdlib import PasswordHash
from dotenv import load_dotenv

load_dotenv()


password_hash = PasswordHash.recommended()




def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_access_token(user_id: int) -> str:
    secret_key = os.getenv("JWT_SECRET_KEY")

    payload = {
        "sub": str(user_id)
    }

    return jwt.encode(payload, secret_key, algorithm="HS256")