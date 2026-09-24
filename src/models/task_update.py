from pydantic import BaseModel

class TaskUpdate(BaseModel):
    title: str
    description: str
    completed: bool
    