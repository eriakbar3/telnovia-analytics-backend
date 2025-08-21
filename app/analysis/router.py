from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import polars as pl

from app import crud, schemas
from app.database import get_db
from app.auth.oauth2 import get_current_user
from app.ai import llm_service # <-- Impor layanan baru
from app.analysis import causal_service # <-- Impor service baru
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
    Menerima query, membaca file data, meneruskannya ke LLM untuk menghasilkan
    kode Polars, mengeksekusi kode tersebut, dan mengembalikan hasilnya.
    """
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

    # 3. Analisis niat pengguna dan jalankan logika yang sesuai
    # Dapatkan skema DataFrame untuk dikirim ke LLM
    df_schema = {col: str(dtype) for col, dtype in df.schema.items()}
    user_query = query_request.query
    
    # Panggil LLM untuk memahami niat pengguna
    intent_data = llm_service.analyze_user_intent(df_schema=df_schema, user_query=user_query)
    intent = intent_data.get("intent")
    variables = intent_data.get("variables")

    ai_reply_str = ""

    # Jalankan logika berdasarkan niat
    if intent == "causal_analysis" and variables:
        # Panggil service analisis kausal
        ai_reply_str = causal_service.estimate_causal_effect(
            df=df,
            treatment=variables.get("treatment"),
            outcome=variables.get("outcome"),
            common_causes=variables.get("common_causes", [])
        )
    elif intent == "descriptive_analysis":
        # Logika yang sudah ada untuk analisis deskriptif
        polars_code = llm_service.generate_polars_code(df_schema=df_schema, user_query=user_query)
        if "ERROR:" in polars_code:
            ai_reply_str = polars_code
        else:
            try:
                # Peringatan: eval() bisa berbahaya. Di lingkungan produksi,
                # ini harus dijalankan dalam sandbox yang sangat terbatas.
                # Variabel 'df' tersedia dalam scope eval().
                result = eval(polars_code)
                
                if isinstance(result, pl.DataFrame):
                    ai_reply_str = result.to_pandas().to_markdown(index=False)
                else:
                    ai_reply_str = str(result)
            except Exception as e:
                ai_reply_str = f"Error executing generated code: {e}"
    else:
        ai_reply_str = "Maaf, saya tidak yakin dengan niat analisis Anda. Coba ajukan pertanyaan deskriptif ('tunjukkan...') atau kausal ('apa dampak dari...')."

    # Simpan percakapan ke database
    crud.create_conversation(
        db=db,
        notebook_id=notebook_id,
        user_query=query_request.query,
        ai_response=ai_reply_str
    )

    return {"reply": ai_reply_str}