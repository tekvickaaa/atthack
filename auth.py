from fastapi import Header, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import Annotated
from models import User
from database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    x_user_username: Annotated[str, Header()],
    db: Session = Depends(get_db)
) -> User:
    """
    Simple authentication dependency.
    Requires X-User-Username header and validates user exists in database.
    """
    if not x_user_username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-User-Username header is required"
        )
    
    user = db.query(User).filter(User.username == x_user_username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User '{x_user_username}' not found"
        )
    
    return user
