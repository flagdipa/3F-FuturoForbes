"""
Pydantic schemas for Tags API
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class EtiquetaBase(BaseModel):
    nombre_etiqueta: str = Field(..., max_length=100)
    color: Optional[str] = Field(None, max_length=7, pattern="^#[0-9A-Fa-f]{6}$")
    activo: int = Field(1, ge=0, le=1)


class EtiquetaCreate(EtiquetaBase):
    pass


class EtiquetaUpdate(BaseModel):
    nombre_etiqueta: Optional[str] = Field(None, max_length=100)
    color: Optional[str] = Field(None, max_length=7, pattern="^#[0-9A-Fa-f]{6}$")
    activo: Optional[int] = Field(None, ge=0, le=1)


class EtiquetaResponse(EtiquetaBase):
    id_etiqueta: int
    
    class Config:
        from_attributes = True


class TransaccionEtiquetaCreate(BaseModel):
    id_etiqueta: int


class TransaccionEtiquetaResponse(BaseModel):
    id_transaccion: int
    id_etiqueta: int
    
    class Config:
        from_attributes = True


class EtiquetaConConteo(EtiquetaResponse):
    """Extended response with usage count"""
    conteo_uso: int = 0
