from fastapi import FastAPI, HTTPException, Depends, Request
from src.models.task import Task
from src.models.task_update import TaskUpdate
from src.database.database import get_db
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.auth import hash_password, verify_password, create_access_token
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
def create_task(task: Task, db: Session = Depends(get_db)):
    result = db.execute(
        text("""
            INSERT INTO tasks (title, description, completed, priority)
            VALUES (:title, :description, :completed, :priority)
            RETURNING *;
        """),
        {
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "priority": task.priority,
        },
    )

    row = result.fetchone()

    db.commit()

    return dict(row._mapping)


@app.get("/tasks")
def get_tasks(db: Session = Depends(get_db)):
    result = db.execute(text("select * from tasks order by id;"))
    tasks = []

    for row in result:
        tasks.append(dict(row._mapping))

    return tasks


@app.get("/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    result = db.execute(
        text("select * from tasks where id=:task_id;"), {"task_id": task_id}
    )
    row = result.fetchone()
    if row:
        task = dict(row._mapping)
        return task

    raise HTTPException(status_code=404, detail="Task not found")


@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated_task: TaskUpdate, db: Session = Depends(get_db)):

    result = db.execute(
        text("""UPDATE tasks SET title=:title, 
    description=:description,
    completed=:completed,
    priority=:priority
    WHERE id=:task_id
    RETURNING *
    
    """),
        {
            "title": updated_task.title,
            "description": updated_task.description,
            "completed": updated_task.completed,
            "priority": updated_task.priority,
            "task_id": task_id,
        },
    )
    row = result.fetchone()
    if row:
        db.commit()
        return dict(row._mapping)

    raise HTTPException(status_code=404, detail="Task not found")


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    result = db.execute(
        text("""
            DELETE FROM tasks
            WHERE id = :task_id
            RETURNING *;
        """),
        {"task_id": task_id},
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
        raise HTTPException(status_code=401, detail="Invalid email or password") #401 code:Unauthorized

    if not verify_password(user.password, existing_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(existing_user.id)

    return {"access_token": access_token, "token_type": "bearer"}
