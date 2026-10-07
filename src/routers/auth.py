import os

import jwt

from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv

from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)

from src.database.database import get_db

from src.models.user import UserRegister, UserLogin, RefreshTokenRequest

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    hashed_password = hash_password(user.password)
    try:
        result = db.execute(
            text("""
            INSERT INTO users (email, password_hash)
            VALUES (:email, :password_hash)
            RETURNING id, email;
        """),
            {"email": user.email, "password_hash": hashed_password},
        )

        user = result.fetchone()
        db.commit()

        return dict(user._mapping)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    result = db.execute(
        text("""
            SELECT id, email, password_hash
            FROM users
            WHERE email = :email;
        """),
        {"email": user.email},
    )

    existing_user = result.fetchone()

    if not existing_user:
        raise HTTPException(
            status_code=401, detail="Invalid email or password"
        )  # 401 code:Unauthorized

    if not verify_password(user.password, existing_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(existing_user.id)
    refresh_token, jti = create_refresh_token(existing_user.id)

    db.execute(
        text("""
        INSERT INTO refresh_tokens (
            jti,
            user_id,
            expires_at
        )
        VALUES (
            :jti,
            :user_id,
            :expires_at
        );
    """),
        {
            "jti": jti,
            "user_id": existing_user.id,
            "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
        }
    )
    db.commit()
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh")
def refresh_token(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    secret_key = os.getenv("JWT_SECRET_KEY")
    refresh_token = data.refresh_token

    try:
        payload = jwt.decode(refresh_token, secret_key, algorithms=["HS256"])

        user_id = payload.get("sub")
        token_type = payload.get("type")
        jti = payload.get("jti")

        if user_id is None or token_type != "refresh" or jti is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        result = db.execute(
            text("""
                SELECT id, user_id, revoked, expires_at
                FROM refresh_tokens
                WHERE jti = :jti;
            """),
            {"jti": jti},
        )

        stored_token = result.fetchone()

        if not stored_token:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        if stored_token.revoked:
            raise HTTPException(
                status_code=401, detail="Refresh token has already been used"
            )

        if stored_token.expires_at <= datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Refresh token has expired")

        db.execute(
            text("""
                UPDATE refresh_tokens
                SET revoked = TRUE
                WHERE jti = :jti;
            """),
            {"jti": jti},
        )

        new_access_token = create_access_token(int(user_id))

        new_refresh_token, new_jti = create_refresh_token(int(user_id))

        db.execute(
            text("""
                INSERT INTO refresh_tokens (
                    jti,
                    user_id,
                    expires_at
                )
                VALUES (
                    :jti,
                    :user_id,
                    :expires_at
                );
            """),
            {
                "jti": new_jti,
                "user_id": int(user_id),
                "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
            },
        )

        db.commit()

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }

    except (jwt.InvalidTokenError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid refresh token")

