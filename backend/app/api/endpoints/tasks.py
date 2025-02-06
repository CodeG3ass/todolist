from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.task import Task, TaskCreate
from app.db.models.task import Task as TaskModel
from sqlalchemy.future import select

router = APIRouter()

@router.post("/", response_model=Task)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    db_task = TaskModel(**task.model_dump())  
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)  
    return db_task

@router.get("/", response_model=list[Task])
async def read_tasks(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    stmt = select(TaskModel).offset(skip).limit(limit)
    result = await db.execute(stmt)
    tasks = result.scalars().all() 
    return tasks