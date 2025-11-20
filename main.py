from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import FastAPI, Depends, WebSocket, HTTPException, status
from database import Base, engine, SessionLocal
from sqlalchemy.orm import Session
from schemas import UserResponse, MeetingResponse
from models import User


@asynccontextmanager
async def lifespan(app: FastAPI):
    #Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine, checkfirst=True)
    yield

app = FastAPI(lifespan=lifespan)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/user")
async def read_users(db: db_dependency):
    users = db.query(User).all()
    return users
@app.get("/user/{username}", response_model=UserResponse)
async def read_user(username: str, db: db_dependency):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@app.put("/user/{username}", response_model=UserResponse)
async def update_user(username: str, updated_user: UserResponse, db: db_dependency):
    pass

@app.post("/transcript", status_code=status.HTTP_202_ACCEPTED)
async def create_transcript(transcript: str, db: db_dependency):
    #if there already is a transcript for the meeting and user, append to it
    pass

