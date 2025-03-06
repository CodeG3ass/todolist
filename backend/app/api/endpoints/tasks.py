from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.task import Task, TaskCreate, TaskResponse
from app.db.models.task import Task as TaskModel
from sqlalchemy.future import select
from fastapi import HTTPException
from app.schemas.user import User
import redis
import json
import os
from app.api.auth import get_current_active_user

router = APIRouter()

# Подключение к Redis
redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis_client = redis.from_url(redis_url)

@router.post("/", response_model=Task)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    db_task = TaskModel(**task.model_dump(), user_id=current_user.id)  # Устанавливаем user_id
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task

@router.get("/", response_model=list[Task])
async def read_tasks(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    cache_key = f"tasks:{skip}:{limit}"
    cached_tasks = redis_client.get(cache_key)
    '''  if cached_tasks:
        tasks = json.loads(cached_tasks)
        return tasks 
    '''
    stmt = select(TaskModel).offset(skip).limit(limit)
    result = await db.execute(stmt)
    tasks = result.scalars().all()

    redis_client.set(cache_key, json.dumps([task.model_dump() for task in tasks]))

    return tasks

@router.post("taskUpdate/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task: TaskCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
     stmt = select(TaskModel).where(TaskModel.id == task_id)
     result = await db.execute(stmt)
     db_task = result.scalar_one_or_none()

     if db_task is None:
         raise HTTPException(status_code=404, detail="Task not found")
     '''
     for key, value in task.dict().items():
        setattr(db_task, key, value)
     '''
     db_task.title = task.title
     db_task.completed = task.completed

     await db.commit()
     await db.refresh(db_task)

     cache_key = f"task:{task_id}"
     redis_client.set(cache_key, 60, json.dumps(db_task.dict()))

     return db_task

@router.delete("/{task_id}", response_model=TaskResponse)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    stmt = select(TaskModel).where(TaskModel.id == task_id)
    result = await db.execute(stmt)
    db_task = result.scalar_one_or_none()

    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    await db.delete(db_task)
    await db.commit()

    cache_key = f"task:{task_id}"
    redis_client.delete(cache_key)

    return {"status": "Task deleted successfully"}