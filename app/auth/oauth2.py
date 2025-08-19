from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.config import settings
from app import crud, schemas
from app.database import get_db

# Skema keamanan ini memberitahu FastAPI endpoint mana yang akan digunakan untuk mendapatkan token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

def create_access_token(data: dict):
    """
    Membuat JSON Web Token (JWT) baru.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> schemas.UserOut:
    """
    Dependency untuk endpoint terproteksi.
    Mendekode token, memvalidasi, dan mengambil data user dari database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Dekode JWT untuk mendapatkan payload
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        # Jika token tidak valid atau ada error saat decode
        raise credentials_exception
    
    # Ambil data user dari database menggunakan email yang ada di dalam token
    user = crud.get_user_by_email(db, email=email)
    
    if user is None:
        # Jika user yang tertera di token tidak ada lagi di database
        raise credentials_exception
        
    return user