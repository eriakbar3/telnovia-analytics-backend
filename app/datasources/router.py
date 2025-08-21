from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas
from app.database import get_db
from app.auth.oauth2 import get_current_user

router = APIRouter(
    prefix="/api/v1/datasources",
    tags=['Data Sources']
)

@router.post("/connections", response_model=schemas.DbConnectionOut)
def create_connection(
    conn_data: schemas.DbConnectionCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    """
    Creates a new data source connection for the current user.
    The connection password is encrypted before being stored.
    """
    return crud.create_db_connection(db=db, conn_data=conn_data, owner_id=current_user.id)

@router.get("/connections", response_model=List[schemas.DbConnectionOut])
def get_connections(
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    return crud.get_db_connections_by_owner(db, owner_id=current_user.id)