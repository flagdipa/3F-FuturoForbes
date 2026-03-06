import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from decimal import Decimal

class Settings(BaseSettings):
    PROJECT_NAME: str = "3F - Futuro Forbes"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    
    # SECURITY
    SECRET_KEY: str = os.getenv("SECRET_KEY", "SUPER_SECRET_KEY_FOR_DEV_ONLY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # DATABASE
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./futuroforbes_v2.db")
    
    # AI
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    
    # PLUGINS
    PLUGINS_DIR: str = "backend/plugins"
    ENABLE_PLUGINS: bool = True

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

settings = Settings()
