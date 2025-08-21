import polars as pl
import pandas as pd
from dowhy import CausalModel

def estimate_causal_effect(
    df: pl.DataFrame, 
    treatment: str, 
    outcome: str, 
    common_causes: list
) -> str:
    """
    Memperkirakan dampak kausal dari variabel treatment terhadap outcome.
    """
    # DoWhy bekerja dengan Pandas, jadi kita konversi terlebih dahulu
    pd_df = df.to_pandas()

    try:
        # 1. Membuat model kausal
        model = CausalModel(
            data=pd_df,
            treatment=treatment,
            outcome=outcome,
            common_causes=common_causes
        )
        
        # 2. Mengidentifikasi estimand (bagaimana cara menghitung efek)
        identified_estimand = model.identify_effect()
        
        # 3. Memperkirakan efek kausal menggunakan regresi linear
        estimate = model.estimate_effect(
            identified_estimand,
            method_name="backdoor.linear_regression"
        )
        
        # 4. Format hasil menjadi kalimat yang mudah dimengerti
        causal_estimate = estimate.value
        result_str = (
            f"Analisis Kausal Diperkirakan:\n"
            f"Perubahan pada '{treatment}' secara rata-rata menyebabkan perubahan sebesar "
            f"{causal_estimate:.2f} pada '{outcome}'."
        )
        return result_str

    except Exception as e:
        return f"Gagal melakukan analisis kausal: {str(e)}. Pastikan nama kolom sudah benar."