from fastapi import FastAPI, HTTPException, Depends
from src.models.task import Task
from src.models.task_update import TaskUpdate
from src.database.database import get_db
from sqlalchemy import text
from sqlalchemy.orm import Session


app = FastAPI(title="Task Manager API")


@app.get("/")
def root():
    return {"message": "Task Manager API is running"}


@app.post("/tasks")
def create_task(task: Task, db: Session = Depends(get_db)):
    result = db.execute(
        text("""
            INSERT INTO tasks (title, description, completed)
            VALUES (:title, :description, :completed)
            RETURNING *;
        """),
        {
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
        },
    )

    row = result.fetchone()

    db.commit()

    return dict(row._mapping)


@app.get("/tasks")
def get_tasks(db: Session = Depends(get_db)):
    result = db.execute(text("select * from tasks;"))
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
    completed=:completed
    WHERE id=:task_id
    RETURNING *
    
    """),
        {
            "title": updated_task.title,
            "description": updated_task.description,
            "completed": updated_task.completed,
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
