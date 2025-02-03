from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.task import Task, TaskCreate
from app.db.models.task import Task as TaskModel

router = APIRouter()

@router.post("/", response_model=Task)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    # Используем model_dump вместо dict
    db_task = TaskModel(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task

@router.get("/", response_model=list[Task])
def read_tasks(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(TaskModel).offset(skip).limit(limit).all()