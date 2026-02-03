"""
Pydantic schemas for Investments/Stocks API
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

class InversionBase(BaseModel):
    id_cuenta: int
    nombre_inversion: str = Field(..., max_length=255)
    simbolo: str = Field(..., max_length=20)
    tipo_inversion: str = Field("Stock")
    cantidad: Decimal = Field(..., max_digits=20, decimal_places=8)
    precio_compra: Decimal = Field(..., max_digits=20, decimal_places=8)
    precio_actual: Decimal = Field(..., max_digits=20, decimal_places=8)
    comision: Decimal = Field(default=0, max_digits=20, decimal_places=8)
    notas: Optional[str] = None
    activo: int = Field(1, ge=0, le=1)

class InversionCreate(InversionBase):
    pass

class InversionUpdate(BaseModel):
    nombre_inversion: Optional[str] = None
    tipo_inversion: Optional[str] = None
    cantidad: Optional[Decimal] = None
    precio_actual: Optional[Decimal] = None
    notas: Optional[str] = None
    activo: Optional[int] = None

class InversionResponse(InversionBase):
    id_inversion: int
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True

class HistorialInversionBase(BaseModel):
    fecha: date
    precio: Decimal = Field(..., max_digits=20, decimal_places=8)

class HistorialInversionCreate(HistorialInversionBase):
    id_inversion: int

class HistorialInversionResponse(HistorialInversionBase):
    id_historial: int
    id_inversion: int
    fecha_creacion: Optional[datetime] = None

    class Config:
        from_attributes = True

class PortfolioSummary(BaseModel):
    total_invested: Decimal
    current_value: Decimal
    total_profit_loss: Decimal
    profit_loss_percentage: Decimal
