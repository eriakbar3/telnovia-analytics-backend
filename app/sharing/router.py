# Buat file baru: telnovia-analytics-backend/app/sharing/router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db

router = APIRouter(
    prefix="/api/v1/public",
    tags=['Public Sharing']
)

@router.get("/notebook/{shareable_token}")
def get_public_notebook_details(shareable_token: str, db: Session = Depends(get_db)):
    notebook = crud.get_notebook_by_token(db, token=shareable_token)
    if not notebook or not notebook.is_public:
        raise HTTPException(status_code=404, detail="Notebook tidak ditemukan atau tidak untuk publik.")

    return {
        "notebook_id": notebook.id,
        "filename": notebook.filename,
        "data_health_report": notebook.health_report
        # Kita tidak sertakan riwayat chat di versi publik untuk saat ini
    }