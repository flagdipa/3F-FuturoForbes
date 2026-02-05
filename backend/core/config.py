"""
Enhanced configuration with strict validation and environment-aware settings.
"""
from pydantic import Field, validator, ConfigDict
from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings with validation"""
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///futuroforbes.db",
        description="Database connection string"
    )
    
    # JWT Configuration
    SECRET_KEY: str = Field(
        ...,
        min_length=32,
        description="JWT secret key - must be at least 32 characters"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, gt=0, description="Token expiration in minutes")
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins"
    )
    
    # Security    
    RATE_LIMIT_PER_MINUTE: int = Field(default=100, gt=0, description="Rate limit per IP per minute")
    
    # Application
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")
    DEBUG: bool = Field(default=True, description="Debug mode")
    
    # API Keys (Optional)
    GOOGLE_AI_API_KEY: Optional[str] = Field(default=None, description="Google Gemini API key for AI features")
    
    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        """Validate database URL format"""
        allowed_prefixes = ("sqlite:///", "postgresql://", "mysql://", "mysql+pymysql://")
        if not v.startswith(allowed_prefixes):
            raise ValueError(
                f"Invalid database URL. Must start with one of: {allowed_prefixes}"
            )
        return v
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        """Validate environment value"""
        allowed = ("development", "staging", "production")
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of: {allowed}")
        return v
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        """Ensure secret key is strong enough"""
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        if v == "your-secret-key-here" or v == "changeme":
            raise ValueError("SECRET_KEY cannot be a default value. Generate a secure random key.")
        return v
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string if needed"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


# Initialize settings (will raise validation error if config is invalid)
try:
    settings = Settings()
except Exception as e:
    print(f"\n❌ CONFIGURATION ERROR:\n{str(e)}\n")
    print("Please check your .env file and ensure all required variables are set correctly.")
    print("\nRequired variables:")
    print("  - SECRET_KEY (at least 32 characters)")
    print("\nOptional variables:")
    print("  - DATABASE_URL (defaults to sqlite:///futuroforbes.db)")
    print("  - CORS_ORIGINS (defaults to localhost:3000,localhost:8000)")
    print("  - ACCESS_TOKEN_EXPIRE_MINUTES (defaults to 30)")
    raise
