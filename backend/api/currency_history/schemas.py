"""
Pydantic schemas for Currency History API
"""
from pydantic import BaseModel, Field, condecimal
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


class HistorialDivisaBase(BaseModel):
    id_divisa: int
    fecha_tasa: date
    tasa_valor: condecimal(max_digits=20, decimal_places=8)
    tipo_actualizacion: int = Field(0, ge=0, le=1)  # 0=Manual, 1=Automatic


class HistorialDivisaCreate(HistorialDivisaBase):
    pass


class HistorialDivisaUpdate(BaseModel):
    tasa_valor: Optional[condecimal(max_digits=20, decimal_places=8)] = None
    tipo_actualizacion: Optional[int] = Field(None, ge=0, le=1)


class HistorialDivisaResponse(HistorialDivisaBase):
    id_historial: int
    fecha_creacion: datetime
    
    class Config:
        from_attributes = True


class ConversionRequest(BaseModel):
    """Request to convert amount between currencies on a specific date"""
    id_divisa_origen: int
    id_divisa_destino: int
    monto: Decimal
    fecha: date


class ConversionResponse(BaseModel):
    """Response with converted amount"""
    monto_original: Decimal
    monto_convertido: Decimal
    tasa_utilizada: Decimal
    fecha_tasa: date
