from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.db.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id= Column(Integer, primary_key= True, index=True)
    username= Column(String, nullable= False, unique= True, index= True)
    password= Column(String, nullable= False)
    nickname= Column(String(30), nullable= False)
    created_at= Column(DateTime(timezone= True), server_default=func.now())
    avatar_image= Column(String, nullable= True)

    role= Column(String, nullable=False, default= "user")

    