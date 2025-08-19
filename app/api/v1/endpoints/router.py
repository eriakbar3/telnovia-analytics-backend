from fastapi import APIRouter, UploadFile, File, HTTPException
import polars as pl
from typing import Dict, Any

router = APIRouter()

MAX_FILE_SIZE_MB = 100
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

def generate_health_report(df: pl.DataFrame) -> Dict[str, Any]:
    """
    Menganalisis DataFrame Polars dan menghasilkan laporan kesehatan data.
    Untuk MVP, ini akan memeriksa nilai yang hilang dan tipe data campuran.
    """
    report = {"columns": []}
    for col_name in df.columns:
        col_series = df[col_name]
        
        # 1. Cek Nilai yang Hilang (Missing Values)
        missing_count = col_series.is_null().sum()
        missing_percentage = (missing_count / len(df)) * 100
        
        # 2. Cek Tipe Data Campuran (Mixed Data Types)
        # Di Polars, tipe 'Object' sering menunjukkan data campuran.
        is_mixed_type = col_series.dtype == pl.Object
        
        column_report = {
            "name": col_name,
            "dtype": str(col_series.dtype),
            "missing_values": {
                "count": missing_count,
                "percentage": round(missing_percentage, 2)
            },
            "warnings": []
        }
        
        if is_mixed_type:
            column_report["warnings"].append("Tipe data campuran terdeteksi.")
            
        report["columns"].append(column_report)
        
    return report


@router.post("/upload", tags=["Data Ingestion"])
async def upload_data_file(file: UploadFile = File(...)):
    """
    Endpoint untuk mengunggah dan memproses file data (CSV atau XLSX).
    Ini akan melakukan parsing awal dan memicu analisis Data Health Report.
    """
    # ... (Validasi ukuran dan tipe file tetap sama) ...
    
    file_extension = file.filename.split('.')[-1].lower()

    try:
        if file_extension == "csv":
            df = pl.read_csv(file.file)
        elif file_extension == "xlsx":
            # Membaca sheet pertama secara default sesuai target MVP
            df = pl.read_excel(file.file, engine='openpyxl')

        # Hasilkan laporan kesehatan dari DataFrame
        health_report = generate_health_report(df)

        return {
            "filename": file.filename,
            "status": "File berhasil dianalisis.",
            "data_health_report": health_report
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan saat memproses file: {str(e)}")
