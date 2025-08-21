# In app/core/security.py
from cryptography.fernet import Fernet
from app.config import settings

# Kunci enkripsi harus dijaga kerahasiaannya, di sini kita ambil dari environment
# Pastikan Anda menambahkan ENCRYPTION_KEY yang kuat di file .env Anda
ENCRYPTION_KEY = settings.encryption_key.encode()
fernet = Fernet(ENCRYPTION_KEY)

def encrypt_password(password: str) -> str:
    return fernet.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password: str) -> str:
    return fernet.decrypt(encrypted_password.encode()).decode()