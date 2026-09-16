from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from typing import List

from database import SessionLocal, engine, Base
from models import Todo, User
from auth import hash_password, verify_password, create_token, verify_token


Base.metadata.create_all(bind=engine)

app = FastAPI()

# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

#Get all todos
@app.get("/todos", response_model= List[TodoOut])
@limiter.limit("60/minute")
async def get_todos(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    todo = db.query(Todo).filter(Todo.user_id == current_user.id).all()

    return todo

#Get one todo
@app.get("/todos/{id}", response_model= TodoOut)
@limiter.limit("60/minute")
async def get_todo(request: Request, id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    todo = db.query(Todo).filter(Todo.id == id, Todo.user_id == current_user.id).first()

    if not todo:
        raise HTTPException(
            status_code = 404,
            detail= "Todo not found"
        )

    return todo

#Create a todo
@app.post("/todos", response_model= TodoOut)
@limiter.limit("60/minute")
async def add_todo(request: Request, data: TodoInput, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    todo = Todo(
        title = data.title,
        description = data.description,
        completed =  data.completed,
        user_id = current_user.id
    )

    db.add(todo)
    db.commit()
    db.refresh(todo)

    return todo

#Update a todo
@app.put("/todos/{id}", response_model= TodoOut)
@limiter.limit("60/minute")
async def update_todo(request: Request, id: int, data: TodoInput, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    todo = db.query(Todo).filter(Todo.id == id, Todo.user_id == current_user.id).first()

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
    
#Delete a todo
@app.delete("/todos/{id}")
@limiter.limit("60/minute")
async def delete_todo(request: Request, id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    todo = db.query(Todo).filter(Todo.id == id, Todo.user_id == current_user.id).first()

    if not todo:
            raise HTTPException(
                status_code = 404,
                detail = "Todo not Found"
            )
    db.delete(todo)
    db.commit()

    return {"message": "Todo deleted"}

#Register a user
@app.post("/auth/register")
@limiter.limit("5/minute")
async def register(request: Request, data: UserRegisterInput, db: Session = Depends(get_db)):
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

#Login and get a token
@app.post("/auth/login", response_model=Token)
@limiter.limit("10/minute")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}