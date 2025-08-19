import os
import shutil
import uuid
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from typing import List
import json # <-- Impor library json
import polars as pl
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.oauth2 import get_current_user
from app import crud, schemas
from app.analysis.data_quality import generate_health_report

router = APIRouter(
    prefix="/api/v1",
    tags=['Notebooks']
)

@router.post("/upload", status_code=201)
def upload_file_and_create_notebook(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    """
    Menangani unggahan file, menyimpannya di server, membuat entri notebook 
    di database, dan mengembalikan notebook_id.
    """
    # Membuat direktori 'uploads' jika belum ada
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Membuat path file yang unik untuk menghindari tumpang tindih nama
    file_path = os.path.join(upload_dir, f"{uuid.uuid4()}-{file.filename}")
    
    # Menyimpan file ke path yang telah ditentukan
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Baca file yang baru diunggah untuk dianalisis
    try:
        df = None
        file_extension = file.filename.split('.')[-1].lower()

        if file_extension == 'csv':
            df = pl.read_csv(file_path)
        elif file_extension == 'xlsx':
            df = pl.read_excel(file_path)
        elif file_extension == 'json': # <-- Logika baru untuk JSON
            # read_json dari Polars bisa secara otomatis meratakan struktur
            df = pl.read_json(file_path)
        else:
            raise HTTPException(status_code=400, detail="Format file tidak didukung.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membaca file untuk analisis: {e}")

    # Hasilkan laporan kualitas data yang sebenarnya
    health_report = generate_health_report(df)

    # Buat entri notebook dengan menyertakan health report
    notebook = crud.create_notebook(
        db=db, 
        filename=file.filename, 
        filepath=file_path, 
        owner_id=current_user.id,
        health_report=health_report # <-- Kirim laporan ke database
    )
    if not notebook:
        raise HTTPException(status_code=500, detail="Gagal membuat notebook di database.")
    
    return {
        "notebook_id": notebook.id,
        "filename": notebook.filename,
        "status": "File berhasil diunggah dan notebook telah dibuat.",
        "data_health_report": health_report # <-- Kirim laporan asli ke frontend
    }

@router.get("/notebook/{notebook_id}")
def get_notebook_details(
    notebook_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    """
    Mengambil detail sebuah notebook berdasarkan ID-nya.
    Memastikan notebook tersebut milik pengguna yang sedang login.
    """
    notebook = crud.get_notebook(db, notebook_id=notebook_id, owner_id=current_user.id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook tidak ditemukan atau Anda tidak memiliki akses.")

    return {
        "notebook_id": notebook.id,
        "filename": notebook.filename,
        "data_health_report": notebook.health_report # <-- Ambil laporan dari database
    }

@router.get("/notebooks", response_model=List[schemas.NotebookOut])
def get_user_notebooks(
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    """
    Mengambil daftar semua notebook milik pengguna yang sedang login.
    """
    notebooks = crud.get_notebooks_by_owner(db, owner_id=current_user.id)
    return notebooks
@router.post("/notebook/{notebook_id}/share")
def toggle_notebook_sharing(
    notebook_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    notebook = crud.get_notebook(db, notebook_id=notebook_id, owner_id=current_user.id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook tidak ditemukan.")

    # Untuk MVP, kita hanya aktifkan sharing, belum ada toggle off
    updated_notebook = crud.update_notebook_sharing(db, notebook, make_public=True)
    return {"shareable_token": updated_notebook.shareable_token}