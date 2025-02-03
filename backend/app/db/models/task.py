from sqlalchemy import Column, Integer, String, Boolean
from app.db.session import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    tittle = Column(String, index=True)
    completed = Column(Boolean, default= False)