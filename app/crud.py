# In telnovia-analytics-backend/app/crud.py

from sqlalchemy.orm import Session
from . import models, schemas
from .auth import utils
import secrets

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = utils.hash_password(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_notebook(db: Session, filename: str, filepath: str, owner_id: int, health_report: dict):
    db_notebook = models.Notebook(
        filename=filename, 
        filepath=filepath, 
        owner_id=owner_id,
        health_report=health_report
    )
    db.add(db_notebook)
    db.commit()
    db.refresh(db_notebook)
    return db_notebook

def get_notebook(db: Session, notebook_id: int, owner_id: int):
    return db.query(models.Notebook).filter(models.Notebook.id == notebook_id, models.Notebook.owner_id == owner_id).first()
def get_notebooks_by_owner(db: Session, owner_id: int):
    return db.query(models.Notebook).filter(models.Notebook.owner_id == owner_id).all()
def create_conversation(db: Session, notebook_id: int, user_query: str, ai_response: str):
    db_conversation = models.Conversation(
        notebook_id=notebook_id,
        user_query=user_query,
        ai_response=ai_response
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

def get_notebook_by_token(db: Session, token: str):
    return db.query(models.Notebook).filter(models.Notebook.shareable_token == token).first()

def update_notebook_sharing(db: Session, notebook: models.Notebook, make_public: bool):
    if make_public and not notebook.shareable_token:
        notebook.shareable_token = secrets.token_urlsafe(16)
    
    notebook.is_public = make_public
    db.commit()
    db.refresh(notebook)
    return notebook