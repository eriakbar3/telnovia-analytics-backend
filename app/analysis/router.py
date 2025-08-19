from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import polars as pl

from app import crud, schemas
from app.database import get_db
from app.auth.oauth2 import get_current_user
import os
import json
router = APIRouter(
    prefix="/api/v1/analysis",
    tags=['Analysis']
)

@router.post("/query", response_model=schemas.QueryResponse)
def handle_query(
    query_request: schemas.QueryRequest, 
    db: Session = Depends(get_db), 
    current_user: schemas.UserOut = Depends(get_current_user)
):
    """
    Menerima query, membaca file data yang sesuai dari notebook,
    melakukan analisis sederhana, dan mengembalikan hasilnya.
    """
    user_query = query_request.query.lower()
    notebook_id = query_request.notebookId
    
    if not notebook_id:
        raise HTTPException(status_code=400, detail="Notebook ID diperlukan untuk analisis.")

    # 1. Mengambil detail notebook dari database untuk mendapatkan path file
    notebook = crud.get_notebook(db, notebook_id=notebook_id, owner_id=current_user.id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook tidak ditemukan.")
    print(f"Notebook found: {notebook.filename} at {notebook.filepath}")
    absolute_file_path = os.path.abspath(notebook.filepath)
    # 2. Membaca file data (CSV atau Excel) menggunakan Polars
    try:
        if notebook.filepath.endswith('.csv'):
            df = pl.read_csv(absolute_file_path)
        elif notebook.filepath.endswith(('.xlsx', '.xls')):
            df = pl.read_excel(absolute_file_path)
        else:
            raise HTTPException(status_code=400, detail="Format file tidak didukung untuk analisis.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membaca file data: {str(e)}")

    # 3. Logika analisis sederhana berbasis kata kunci
    ai_reply = None
    df_result = None
    ai_reply_str = ""
    print(f"User query: {user_query}")
    if "describe" in user_query or "summary" in user_query:
        # Mengembalikan statistik deskriptif dari data
        df_result = df.describe()
    elif "head" in user_query or "show first" in user_query:
        # Mengembalikan 5 baris pertama dari data
        df_result = df.head(5)
    else:
        df_result = "Perintah tidak dikenali. Coba 'describe' atau 'head'."
    if df_result is not None:
        # Konversi Polars DataFrame ke Pandas DataFrame, lalu ke Markdown
        ai_reply_str = df_result.to_pandas().to_markdown(index=False)

    # Simpan percakapan ke database setelah mendapatkan jawaban
    if notebook_id:
        crud.create_conversation(
            db=db,
            notebook_id=notebook_id,
            user_query=query_request.query,
            ai_response=ai_reply_str
        )

    return {"reply": ai_reply_str}