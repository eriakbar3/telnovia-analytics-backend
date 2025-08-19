import polars as pl

def generate_health_report(df: pl.DataFrame) -> dict:
    """
    Menganalisis DataFrame Polars dan menghasilkan laporan kualitas data yang komprehensif,
    termasuk deteksi anomali dasar.
    """
    report = {"columns": []}
    num_rows = len(df)

    for col_name in df.columns:
        col_series = df[col_name]
        col_dtype = str(col_series.dtype)
        warnings = []
        
        # Inisialisasi dictionary untuk anomali
        anomaly_report = { "detected": False, "count": 0, "method": None }

        # 1. Cek nilai kosong (missing values)
        missing_count = col_series.is_null().sum()
        missing_percentage = (missing_count / num_rows) * 100 if num_rows > 0 else 0

        # 2. Cek tipe data campuran (mixed data types)
        if col_dtype == 'Object':
            warnings.append("Tipe data campuran terdeteksi.")

        # 3. Cek kardinalitas tinggi (high-cardinality)
        if col_series.dtype in [pl.Utf8, pl.Object]:
            unique_count = col_series.n_unique()
            if num_rows > 0 and (unique_count / num_rows) > 0.9:
                warnings.append(f"Kardinalitas tinggi ({unique_count} nilai unik).")

        # 4. Cek varians rendah (low-variance)
        if col_series.n_unique() == 1:
            warnings.append("Varians rendah (semua nilai sama).")
        
        # --- 5. DETEKSI ANOMALI BARU ---
        # Lakukan hanya untuk kolom numerik
        if col_series.dtype in pl.NUMERIC_DTYPES:
            # Pastikan kolom tidak kosong untuk perhitungan kuantil
            if not col_series.is_null().all():
                q1 = col_series.quantile(0.25)
                q3 = col_series.quantile(0.75)
                if q1 is not None and q3 is not None:
                    iqr = q3 - q1
                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr
                    
                    # Hitung jumlah outliers
                    outliers_count = df.filter(
                        (col_series < lower_bound) | (col_series > upper_bound)
                    ).height
                    
                    if outliers_count > 0:
                        anomaly_report["detected"] = True
                        anomaly_report["count"] = outliers_count
                        anomaly_report["method"] = "IQR"
        
        column_report = {
            "name": col_name,
            "dtype": col_dtype,
            "missing_values": {
                "count": missing_count,
                "percentage": round(missing_percentage, 2)
            },
            "warnings": warnings,
            "anomaly_report": anomaly_report # <-- Tambahkan hasil deteksi anomali
        }
        report["columns"].append(column_report)
        
    return report