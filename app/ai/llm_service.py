from openai import OpenAI
from app.config import settings
import polars as pl
import json
client = OpenAI(api_key=settings.openai_api_key)

def generate_polars_code(df_schema: dict, user_query: str) -> str:
    """
    Mengirimkan prompt ke API GPT-5 untuk mengubah pertanyaan pengguna menjadi kode Polars.
    """
    
    # Rekayasa Prompt (Prompt Engineering)
    system_prompt = f"""
    You are an expert data analyst who specializes in the Python **Polars** library.
    A user will provide you with a data schema and a natural language query.
    Your task is to convert the user's query into a single, executable line of Polars code that operates on a DataFrame named 'df'.

    **Crucial: You must use Polars syntax only.** For grouping and aggregation, use `.group_by('column').agg(...)`, NOT `.groupby()`.

    The schema of the DataFrame 'df' is: {df_schema}.
    Only return the Polars code, without any explanation, import statements, or markdown formatting.
    Example query: "show total sales per product"
    Example Polars code for the query: "df.group_by('product').agg(pl.sum('sales'))"
    
    If the query cannot be answered with the given schema, return "ERROR: Query cannot be answered."
    """

    response = client.chat.completions.create(
        model="gpt-5-chat-latest",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        temperature=0,
    )
    
    generated_code = response.choices[0].message.content
    return generated_code

def analyze_user_intent(df_schema: dict, user_query: str) -> dict:
    """
    Menggunakan GPT-5 untuk menganalisis niat pengguna.
    """
    system_prompt = f"""
    You are an expert analytical system. Your job is to analyze a user's query about a dataset and determine their intent.
    The dataset schema is: {df_schema}.

    Analyze the user's query and return a JSON object with the following structure:
    - "intent": Can be "descriptive_analysis" (for queries like 'show', 'describe', 'list') OR "causal_analysis" (for queries asking 'what is the effect of', 'impact of', 'why did X change').
    - "variables": 
        - If intent is "descriptive_analysis", this should be null.
        - If intent is "causal_analysis", this should be a JSON object containing "treatment", "outcome", and "common_causes" identified from the query and schema.

    User Query: "{user_query}"
    """

    response = client.chat.completions.create(
        model="gpt-5-chat-latest",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt}
        ]
    )
    
    intent_data = json.loads(response.choices[0].message.content)
    return intent_data
