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


# Modifikasi `Notebook` untuk tidak memerlukan file
def create_notebook_from_db(db: Session, conn: models.DataSourceConnection, owner_id: int):
    notebook_name = f"Analisis dari {conn.name}"
    # Kita tidak menyimpan file, jadi filepath bisa null atau menunjuk ke info koneksi
    db_notebook = models.Notebook(
        filename=notebook_name,
        filepath=f"db_connection_{conn.id}",
        owner_id=owner_id,
        health_report={}  # Health report akan dihasilkan nanti
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

from app.core.security import encrypt_password, decrypt_password # <-- Impor decrypt

def create_db_connection(db: Session, conn_data: schemas.DbConnectionCreate, owner_id: int):
    encrypted_pass = encrypt_password(conn_data.password)
    db_conn = models.DataSourceConnection(
        name=conn_data.name, host=conn_data.host, port=conn_data.port,
        username=conn_data.username, encrypted_password=encrypted_pass,
        dbname=conn_data.dbname, owner_id=owner_id
    )
    db.add(db_conn)
    db.commit()
    db.refresh(db_conn)
    return db_conn

def get_db_connections_by_owner(db: Session, owner_id: int):
    return db.query(models.DataSourceConnection).filter(models.DataSourceConnection.owner_id == owner_id).all()

def get_db_connection(db: Session, conn_id: int, owner_id: int):
    return db.query(models.DataSourceConnection).filter(
        models.DataSourceConnection.id == conn_id,
        models.DataSourceConnection.owner_id == owner_id
    ).first()
def create_team_for_user(db: Session, user: models.User):
    """Membuat tim baru saat pengguna mendaftar dan menjadikannya Admin."""
    team_name = f"{user.email.split('@')[0]}'s Team"
    new_team = models.Team(name=team_name)
    db.add(new_team)
    db.commit()
    db.refresh(new_team)

    membership = models.TeamMembership(
        user_id=user.id,
        team_id=new_team.id,
        role=models.RoleEnum.admin # Jadikan pendaftar sebagai Admin
    )
    db.add(membership)
    db.commit()
    return new_team
def get_team_members(db: Session, team_id: int):
    return db.query(models.TeamMembership).filter(models.TeamMembership.team_id == team_id).all()

def add_user_to_team(db: Session, team_id: int, user_id: int, role: models.RoleEnum):
    membership = models.TeamMembership(
        team_id=team_id,
        user_id=user_id,
        role=role
    )
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership

def get_user_membership_in_team(db: Session, user_id: int, team_id: int):
    return db.query(models.TeamMembership).filter(
        models.TeamMembership.user_id == user_id,
        models.TeamMembership.team_id == team_id
    ).first()