from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated


from database import SessionLocal
from sqlalchemy.orm import Session

from models import Users
from .auth import get_current_user

router = APIRouter(
    prefix="/user",
    tags=["user"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]
user_dependency = Annotated[Users,Depends(get_current_user)]

@router.get("/")
async def get_users(db:db_dependency):
    return db.query(Users).all()