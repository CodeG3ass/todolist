from fastapi import FastAPI
from app.api.endpoints import tasks, users
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import engine
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.task import Task
from app.db.session import AsyncSessionLocal, startup, shutdown
from app.db.models.user import User
from app.db.session import Base

# Создание базы данных

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    await startup()

# Закрытие соединений при завершении
@app.on_event("shutdown")
async def on_shutdown():
    await shutdown()

# Зависимость для получения асинхронной сессии
async def get_db():
    async with AsyncSessionLocal() as db:
        yield db

# Подключение маршрутов
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(users.router, prefix="/users", tags=["users"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Todo API!"}