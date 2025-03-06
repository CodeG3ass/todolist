from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.user import User, UserCreate
from app.db.models.user import User as UserModel
from sqlalchemy.future import select
from app.api.auth import get_password_hash
#from app.core.security import hash_password  # Предполагается, что у вас есть функция для хеширования паролей

router = APIRouter()

@router.post("/", response_model=User)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Проверка на существование пользователя с таким же именем
    stmt_existing_user = select(UserModel).filter(UserModel.username == user.username)
    result = await db.execute(stmt_existing_user)
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(username=user.username, email=user.email, password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user

@router.get("/", response_model=list[User])
async def read_users(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    stmt = select(UserModel).offset(skip).limit(limit)
    result = await db.execute(stmt)
    tasks = result.scalars().all() 
    return tasks
