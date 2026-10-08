from pydantic import BaseModel

class Task(BaseModel):
    id: int 
    title: str
    description: str
    completed: bool 
    priority: int | None = None

class TaskCreate(BaseModel):
    title: str
    description: str
    completed: bool = False
    priority: int | None = None