from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from typing import List

from database import SessionLocal, engine, Base
from models import Todo, User
from auth import hash_password, verify_password, create_token, verify_token

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

class TodoInput(BaseModel):
    
    title: str
    description: str
    completed: bool=False

class TodoOut(BaseModel):
    model_config = ConfigDict(from_attributes = True)

    id: int
    title: str
    description: str
    completed: bool

class UserRegisterInput(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        username = verify_token(token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

#GET    /todos          → get all todos
@app.get("/todos", response_model= List[TodoOut])
def get_todos(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    return db.query(Todo).all()

#GET    /todos/{id}     → get one todo
@app.get("/todos/{id}", response_model= TodoOut)
def get_todo(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    todo = db.query(Todo).filter(Todo.id == id).first()

    if not todo:
        raise HTTPException(
            status_code = 404,
            detail= "Todo not found"
        )

    return todo

#POST   /todos          → create a todo
@app.post("/todos", response_model= TodoOut)
def add_todo(data: TodoInput, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    todo = Todo(
        title = data.title,
        description = data.description,
        completed =  data.completed
    )

    db.add(todo)
    db.commit()
    db.refresh(todo)

    return todo

#PUT    /todos/{id}     → mark as completed
@app.put("/todos/{id}", response_model= TodoOut)
def update_todo(id: int, data: TodoInput, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    todo = db.query(Todo).filter(Todo.id == id).first()

    if not todo:
        raise HTTPException(
            status_code = 404,
            detail = "Todo not Found"
        )

    todo.title = data.title
    todo.description = data.description
    todo.completed =  data.completed

    db.commit()
    db.refresh(todo)

    return todo
    
#DELETE /todos/{id}     → delete a todo
@app.delete("/todos/{id}")
def delete_todo(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    todo = db.query(Todo).filter(Todo.id == id).first()

    if not todo:
            raise HTTPException(
                status_code = 404,
                detail = "Todo not Found"
            )
    db.delete(todo)
    db.commit()

    return {"message": "Todo deleted"}

#POST   /auth/register  → register a user
@app.post("/auth/register")
def register(data: UserRegisterInput, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    user = User(
        username=data.username,
        hashed_password=hash_password(data.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User registered successfully"}

#POST   /auth/login     → login and get a token
@app.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}