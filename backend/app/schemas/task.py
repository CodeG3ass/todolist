from pydantic import BaseModel

class TaskBase(BaseModel):
    title: str
    completed: bool = False
    description: str = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: str = None
    completed: bool = None
    description: str = None

class TaskResponse(TaskBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

class Task(TaskBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True