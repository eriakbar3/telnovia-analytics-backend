# In telnovia-analytics-backend/app/models.py
import enum
from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Text, Boolean, Enum # <-- Impor Enum
from sqlalchemy.orm import relationship
from .database import Base

# Definisikan Enum untuk peran agar konsisten
class RoleEnum(enum.Enum):
    admin = "Admin"
    editor = "Editor"
    viewer = "Viewer"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    # Hubungan baru ke keanggotaan tim
    memberships = relationship("TeamMembership", back_populates="user")

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    
    members = relationship("TeamMembership", back_populates="team")
    notebooks = relationship("Notebook", back_populates="team")
    data_source_connections = relationship("DataSourceConnection", back_populates="team")

class TeamMembership(Base):
    __tablename__ = "team_memberships"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"), primary_key=True)
    role = Column(Enum(RoleEnum), nullable=False)
    
    user = relationship("User", back_populates="memberships")
    team = relationship("Team", back_populates="members")

class Notebook(Base):
    __tablename__ = "notebooks"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    filepath = Column(String, unique=True)
    health_report = Column(JSON, nullable=True)
    shareable_token = Column(String, unique=True, index=True, nullable=True)
    is_public = Column(Boolean, server_default="false", nullable=False)

    # Ganti owner_id menjadi team_id
    team_id = Column(Integer, ForeignKey("teams.id"))
    team = relationship("Team", back_populates="notebooks")
    conversations = relationship("Conversation", back_populates="notebook")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    notebook_id = Column(Integer, ForeignKey("notebooks.id"))
    user_query = Column(String)
    ai_response = Column(Text) # Menggunakan Text untuk menyimpan Markdown yang bisa jadi panjang

    notebook = relationship("Notebook", back_populates="conversations")
class DataSourceConnection(Base):
    __tablename__ = "data_source_connections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    db_type = Column(String, default="PostgreSQL")
    host = Column(String)
    port = Column(Integer)
    username = Column(String)
    encrypted_password = Column(String)
    dbname = Column(String)
    
    # Ganti owner_id menjadi team_id
    team_id = Column(Integer, ForeignKey("teams.id"))
    team = relationship("Team", back_populates="data_source_connections")