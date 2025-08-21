# In telnovia-analytics-backend/app/auth/router.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from . import utils, oauth2

router = APIRouter(
    prefix="/api/v1/auth",  # Menambahkan prefix untuk semua rute di file ini
    tags=['Authentication']
)

@router.post("/register", response_model=schemas.UserOut)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")
    
    new_user = crud.create_user(db=db, user=user)
    
    # --- PERUBAHAN DI SINI ---
    # Buat tim baru untuk pengguna yang baru mendaftar
    crud.create_team_for_user(db=db, user=new_user)
    
    return new_user


@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login pengguna dan mengembalikan access token.
    Memverifikasi email dan password, lalu membuat JWT jika valid.
    """
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = oauth2.create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}