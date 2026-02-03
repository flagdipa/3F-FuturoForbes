from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os

class Settings(BaseSettings):
    # Usamos SettingsConfigDict para Pydantic V2
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "..", "..", ".env"),
        env_file_encoding='utf-8',
        extra='ignore' # Ignorar variables extra en el .env
    )
    
    PROJECT_NAME: str = "Fer Futuro Forbes (3F)"
    
    # Estos se cargarán desde el .env o el entorno
    DATABASE_URL: str = "mysql+pymysql://root:Fer21gon@localhost:3306/futuroforbes_db"
    SECRET_KEY: str = "7fe8a3b2c1d0e9f8a7b6c5d4e3f2a1b0"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]

settings = Settings()
