from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import schemas
from app.auth.oauth2 import get_current_user

router = APIRouter(
    prefix="/api/v1",
    tags=['Users']
)

@router.get("/users/me", response_model=schemas.UserOut)
def read_users_me(current_user: schemas.UserOut = Depends(get_current_user)):
    """
    Endpoint terproteksi untuk mendapatkan detail pengguna yang sedang login.
    Fungsi `get_current_user` sebagai dependency akan menangani semua validasi token.
    """
    return current_user