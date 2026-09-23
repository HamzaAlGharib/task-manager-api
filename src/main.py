from fastapi import FastAPI
from src.models.task import Task

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