from fastapi import FastAPI, HTTPException
from src.models.task import Task
from src.models.task_update import TaskUpdate

app = FastAPI(title="Task Manager API")

tasks = []
next_task_id = 1

@app.get("/")
def root():
    return {"message":"Task Manager API is running"}

@app.post("/tasks")
def create_task(task: Task):
    global next_task_id
    task.id = next_task_id
    next_task_id += 1

    tasks.append(task)
    return task

@app.get("/tasks")
def get_tasks():
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

        
