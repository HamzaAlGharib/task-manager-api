from pydantic import BaseModel

class Task(BaseModel):
    id: int = 0
    title: str
    description: str
    completed: bool = False