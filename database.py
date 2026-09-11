from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# This creates a students.db file in your project folder
DATABASE_URL = "sqlite:///E:/Python Backend/FastAPI/todo_api/todos.db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass