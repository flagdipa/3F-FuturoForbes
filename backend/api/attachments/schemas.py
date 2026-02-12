"""
Pydantic schemas for Attachments API
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AdjuntoBase(BaseModel):
    tipo_referencia: str = Field(..., max_length=50)
    id_referencia: int
    descripcion: Optional[str] = None


class AdjuntoCreate(AdjuntoBase):
    pass


class AdjuntoResponse(AdjuntoBase):
    id_adjunto: int
    nombre_archivo: str
    ruta_archivo: str
    tipo_mime: Optional[str]
    tamaño_bytes: Optional[int]
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime]
    url_descarga: Optional[str] = None  # Computed field
    
    class Config:
        from_attributes = True


class AdjuntoUpdate(BaseModel):
    descripcion: Optional[str] = None
