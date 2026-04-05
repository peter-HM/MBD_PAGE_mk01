from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, func

from app.db.database import Base

class Project(Base):
    __tablename__= "projects"

    id= Column(Integer, primary_key= True, index= True)

    name= Column(String, nullable= False)
    summary= Column(String, nullable= False)
    description= Column(Text, nullable= False) 

    image_path = Column(String, nullable=False, default="")

    stack = Column(String, nullable=False, default="")
    status = Column(String, nullable=False, default="planning")

    demo_url = Column(String, nullable=True)
    github_url = Column(String, nullable=True)

    is_public = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


    