import os
import jwt

from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, HTTPException, Depends, Request
from src.models.task import Task
from src.models.task_update import TaskUpdate
from src.database.database import get_db
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_user,
)
from src.models.user import UserRegister
from sqlalchemy.exc import IntegrityError
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI(title="Task Manager API")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []

    for error in exc.errors():
        message = error["msg"]

        if message.startswith("Value error, "):
            message = message.removeprefix("Value error, ")

        errors.append(message)

    return JSONResponse(status_code=422, content={"detail": errors})


@app.get("/")
def root():
    return {"message": "Task Manager API is running"}


@app.post("/tasks")
def create_task(
    task: Task,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    result = db.execute(
        text("""
            INSERT INTO tasks (title, description, completed, priority, user_id)
            VALUES (:title, :description, :completed, :priority, :user_id)
            RETURNING id, title, description, completed, priority;
        """),
        {
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "priority": task.priority,
            "user_id": current_user_id,
        },
    )

    row = result.fetchone()

    db.commit()

    return dict(row._mapping)


@app.get("/tasks")
def get_tasks(
    db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user)
):
    result = db.execute(
        text(
            "select id, title, description, completed, priority from tasks where user_id=:user_id order by id;"
        ),
        {"user_id": current_user_id},
    )
    tasks = []

    for row in result:
        tasks.append(dict(row._mapping))

    return tasks


@app.get("/tasks/{task_id}")
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    result = db.execute(
        text(
            "select id, title, description, completed, priority from tasks where id=:task_id AND user_id= :user_id;"
        ),
        {"task_id": task_id, "user_id": current_user_id},
    )
    row = result.fetchone()
    if row:
        task = dict(row._mapping)
        return task

    raise HTTPException(status_code=404, detail="Task not found")


@app.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    updated_task: TaskUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):

    result = db.execute(
        text("""UPDATE tasks SET title=:title, 
    description=:description,
    completed=:completed,
    priority=:priority
    WHERE id=:task_id AND user_id = :user_id
    RETURNING id, title, description, completed, priority;
    
    """),
        {
            "title": updated_task.title,
            "description": updated_task.description,
            "completed": updated_task.completed,
            "priority": updated_task.priority,
            "task_id": task_id,
            "user_id": current_user_id,
        },
    )
    row = result.fetchone()
    if row:
        db.commit()
        return dict(row._mapping)

    raise HTTPException(status_code=404, detail="Task not found")


@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    result = db.execute(
        text("""
            DELETE FROM tasks
            WHERE id = :task_id AND user_id = :user_id
            RETURNING id, title, description, completed, priority;
        """),
        {"task_id": task_id, "user_id": current_user_id},
    )

    row = result.fetchone()

    if row:
        db.commit()
        return dict(row._mapping)

    raise HTTPException(status_code=404, detail="Task not found")


@app.post("/auth/register")
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


@app.post("/auth/login")
def login(user: UserRegister, db: Session = Depends(get_db)):
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


@app.post("/auth/refresh")
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    secret_key = os.getenv("JWT_SECRET_KEY")

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
