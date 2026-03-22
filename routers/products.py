import string

from fastapi import APIRouter, Depends, HTTPException
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from models import Products
from starlette import status
from fastapi.params import Path

from .auth import get_current_user

router = APIRouter(
    prefix="/product",
    tags=["product"],
)


def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()


db_dependency = Annotated[Session,Depends(get_db)]
user_dependency = Annotated[dict,Depends(get_current_user)]

class ProductRequest(BaseModel):
  name: str
  description: str
  price: str
  category: str
  quantity: int

@router.post("/",status_code= status.HTTP_201_CREATED)
async def create_product(user:user_dependency,db:db_dependency,product_request: ProductRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    product_model =Products(**product_request.model_dump())
    db.add(product_model)
    db.commit()

@router.get("/",status_code= status.HTTP_200_OK)
async def get_product(user:user_dependency,db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Products).all()

@router.put('/{product_id}',status_code= status.HTTP_200_OK)
async def update_product(user:user_dependency,db:db_dependency,product_request: ProductRequest,product_id:int):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    product_model = db.query(Products).filter(Products.id == product_id).first()
    if product_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Product not found")
    product_model.name = product_request.name
    product_model.description = product_request.description
    product_model.price = product_request.price
    product_model.category = product_request.category
    product_model.quantity = product_request.quantity
    db.add(product_model)
    db.commit()

@router.delete('/{product_id}',status_code= status.HTTP_204_NO_CONTENT)
async def delete_product(user:user_dependency,db:db_dependency,product_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    product_model = db.query(Products).filter(Products.id == product_id).first()
    if product_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Product not found")
    db.query(Products).filter(Products.id == product_id).delete()
    db.commit()

@router.get('/{product_id}',status_code= status.HTTP_200_OK)
async def get_product(user:user_dependency,db:db_dependency,product_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Products).filter(Products.id == product_id).first()