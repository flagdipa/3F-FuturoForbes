"""
Pydantic schemas for System Configuration API
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ConfigBase(BaseModel):
    clave: str = Field(..., max_length=100, description="Unique setting key")
    valor: str = Field(..., max_length=255, description="Setting value as string")
    descripcion: Optional[str] = Field(None, description="Detailed explanation of the setting")

class ConfigUpdate(BaseModel):
    valor: str = Field(..., max_length=255)
    descripcion: Optional[str] = None

class ConfigResponse(ConfigBase):
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True
