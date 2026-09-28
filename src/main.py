from fastapi import FastAPI, HTTPException
from src.models.task import Task
from src.models.task_update import TaskUpdate
from src.database.database import SessionLocal
from sqlalchemy import text

app = FastAPI(title="Task Manager API")

db = SessionLocal()

tasks = []
next_task_id = 1

@app.get("/")
def root():
    return {"message":"Task Manager API is running"}

@app.post("/tasks")
def create_task(task: Task):
    result = db.execute(
        text("""
            INSERT INTO tasks (title, description, completed)
            VALUES (:title, :description, :completed)
            RETURNING *;
        """),
        {
            "title": task.title,
            "description": task.description,
            "completed": task.completed
        }
    )

    row = result.fetchone()

    db.commit()

    return dict(row._mapping)

@app.get("/tasks")
def get_tasks():
    result = db.execute(text("select * from tasks;"))
    tasks = []

    for row in result:
        tasks.append(dict(row._mapping))

    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task.id == task_id:
            return task
        
    raise HTTPException(status_code=404, detail="Task not found")

@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated_task: TaskUpdate):
    for task in tasks:
        if task.id == task_id:
            task.title = updated_task.title
            task.description = updated_task.description
            task.completed = updated_task.completed
            return task

    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    for task in tasks:
        if task.id == task_id:
            tasks.remove(task)
            return

    raise HTTPException(status_code=404, detail="Task not found")

        
