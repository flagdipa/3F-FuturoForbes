"""
Pydantic schemas for Assets (Activos) API
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

class ActivoBase(BaseModel):
    nombre_activo: str = Field(..., max_length=255)
    tipo_activo: str
    valor_inicial: Decimal = Field(..., max_digits=20, decimal_places=8)
    valor_actual: Decimal = Field(..., max_digits=20, decimal_places=8)
    fecha_compra: Optional[date] = None
    notas: Optional[str] = None
    tasa_variacion: Decimal = Field(default=0, max_digits=10, decimal_places=4)
    metodo_variacion: str = Field(default="None") # Linear, Percentage, None
    frecuencia_variacion: str = Field(default="Yearly")
    activo: int = Field(1, ge=0, le=1)

class ActivoCreate(ActivoBase):
    pass

class ActivoUpdate(BaseModel):
    nombre_activo: Optional[str] = None
    tipo_activo: Optional[str] = None
    valor_actual: Optional[Decimal] = None
    notas: Optional[str] = None
    tasa_variacion: Optional[Decimal] = None
    metodo_variacion: Optional[str] = None
    frecuencia_variacion: Optional[str] = None
    activo: Optional[int] = None

class ActivoResponse(ActivoBase):
    id_activo: int
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True

class HistorialActivoBase(BaseModel):
    fecha: date
    valor: Decimal = Field(..., max_digits=20, decimal_places=8)
    notas: Optional[str] = None

class HistorialActivoCreate(HistorialActivoBase):
    id_activo: int

class HistorialActivoResponse(HistorialActivoBase):
    id_historial: int
    id_activo: int
    fecha_creacion: Optional[datetime] = None

    class Config:
        from_attributes = True
