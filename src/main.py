from fastapi import FastAPI
from src.models.task import Task

app = FastAPI(title="Task Manager API")

@app.get("/")
def root():
    return {"message":"Task Manager API is running"}

@app.post("/tasks")
def create_task(task: Task):
    return task