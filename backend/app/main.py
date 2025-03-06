from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.auth import authenticate_user, create_access_token, get_current_active_user, Token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_active_user
from app.api.endpoints import tasks, users
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import engine
from app.db.models.task import Task
from app.db.session import AsyncSessionLocal, startup, shutdown
from app.db.models.user import User
from app.db.session import Base
import redis
import os

# Создание базы данных

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение к Redis
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 0))
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

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

app.include_router(tasks.router, prefix="/tasks", tags=["tasks"], dependencies=[Depends(get_current_active_user)])
app.include_router(users.router, prefix="/users", tags=["users"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Todo API!"}