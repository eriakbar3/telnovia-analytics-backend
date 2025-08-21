# In telnovia-analytics-backend/app/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database configuration variables
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    # Key for encrypting/decrypting sensitive data like connection passwords
    encryption_key: str
    
    openai_api_key: str
    
    class Config:
        env_file = ".env" # Specifies the file to load variables from

# Create a single instance to be used across the application
settings = Settings()