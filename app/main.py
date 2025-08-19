from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine

# Impor semua router yang aktif
from app.auth.router import router as auth_router 
from app.users.router import router as users_router
from app.analysis.router import router as analysis_router
from app.notebooks.router import router as notebook_router
from app.presentation.router import router as presentation_router
from app.sharing.router import router as sharing_router

# Membuat tabel di database (jika belum ada) saat aplikasi dimulai
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Telnovia Analytics Backend",
    version="1.0.0"
)

# Konfigurasi CORS
origins = [
    "http://localhost:3000", # Alamat frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mendaftarkan semua modul API ke aplikasi utama
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(analysis_router)
app.include_router(notebook_router)
app.include_router(presentation_router)
app.include_router(sharing_router) 
@app.get("/")
def read_root():
    """
    Endpoint root untuk memeriksa apakah server berjalan.
    """
    return {"message": "Welcome to Telnovia Backend"}