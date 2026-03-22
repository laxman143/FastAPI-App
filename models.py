from database import Base
from sqlalchemy import Column, Integer, String, Boolean,ForeignKey

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)
    phone_number = Column(String)

class Products(Base):
    __tablename__ = 'products'
    id = Column(Integer,primary_key=True)
    name = Column(String)
    description = Column(String)
    price = Column(String)
    category = Column(String)
    quantity = Column(Integer)
    owner_id = Column(Integer, ForeignKey('users.id'))