from datetime import timedelta, timezone,datetime


from fastapi import Depends, HTTPException, APIRouter
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy import String
from starlette import status

from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session

from models import Users
from jose import jwt,JWTError

router = APIRouter(
prefix="/auth",
tags=["auth"],
)

SECRET_KEY = "TGhVMJeY75AJaZaA4U47NV44TbiGTLZ11vMjeb5EPyc="
ALGORITHM = "HS256"
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str
    first_name:str
    last_name:str
    role :str
    phone_number : str

class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()

db_dependency = Annotated[Session,Depends(get_db)]

def authenticate_user( username: str, password: str,db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

@router.post("/",status_code=status.HTTP_201_CREATED)
async def create_user(db:db_dependency,create_user_request:CreateUserRequest):
    hashed_password = bcrypt_context.hash(create_user_request.password)
    create_user_model = Users(
        username=create_user_request.username,
        email=create_user_request.email,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        phone_number=create_user_request.phone_number,
        hashed_password=hashed_password,
        is_active = True
    )
    print(create_user_model)
    db.add(create_user_model)
    db.commit()

def create_access_token(username:str,user_id:str,role:str,expires_delta:timedelta):
    encode = {'sub' : username, 'id': user_id , 'role': role}
    expires = datetime.now(timezone.utc)  + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode,SECRET_KEY,algorithm='HS256')

@router.post("/token",response_model=Token)
async def login_for_access_token(formData: Annotated[OAuth2PasswordRequestForm,Depends()],db:db_dependency):
    print(formData)
    user = authenticate_user(username=formData.username,password=formData.password,db = db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate user")
    token = create_access_token(user.username,user.id,user.role,timedelta(minutes=30))
    return {"access_token":token,"token_type":"bearer"}

async def get_current_user(token: Annotated[str,Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=['HS256'])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise  HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail= "Could not validate user")
        return {'username':username,'id':user_id, 'user_role':user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")