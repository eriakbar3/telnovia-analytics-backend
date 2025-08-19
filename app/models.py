# In telnovia-analytics-backend/app/models.py
from sqlalchemy import Column, Integer, String,ForeignKey,JSON, Text,Boolean 
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    notebooks = relationship("Notebook", back_populates="owner")

class Notebook(Base):
    __tablename__ = "notebooks"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    filepath = Column(String, unique=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    health_report = Column(JSON, nullable=True)
    shareable_token = Column(String, unique=True, index=True, nullable=True)
    is_public = Column(Boolean, server_default='f', nullable=False)

    owner = relationship("User", back_populates="notebooks")
    conversations = relationship("Conversation", back_populates="notebook")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    notebook_id = Column(Integer, ForeignKey("notebooks.id"))
    user_query = Column(String)
    ai_response = Column(Text) # Menggunakan Text untuk menyimpan Markdown yang bisa jadi panjang

    notebook = relationship("Notebook", back_populates="conversations")
