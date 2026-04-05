from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey, Boolean

from app.db.database import Base

class Post(Base):
    __tablename__ = "posts"

    id= Column(Integer, primary_key= True, index=True)
    author_id= Column(Integer, ForeignKey("users.id"), nullable= False)
    title= Column(String, nullable= False)
    body= Column(Text, nullable= False)

    url= Column(String, nullable= False, default="#")
    image_path= Column(String , nullable= False)

    is_public= Column(Boolean, nullable= False, default= True)
    cat= Column(String, nullable= False)
    cat_detail= Column(String, nullable= False)

    created_at= Column(DateTime(timezone= True), server_default=func.now())
    updated_at= Column(DateTime(timezone= True), server_default= func.now(), onupdate= func.now())