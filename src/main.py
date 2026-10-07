
from src.routers.auth import router as auth_router
from fastapi import FastAPI, HTTPException, Depends, Request
from src.models.task import Task
from src.models.task_update import TaskUpdate
from src.database.database import get_db
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.auth import get_current_user
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI(title="Task Manager API")

app.include_router(auth_router)


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


