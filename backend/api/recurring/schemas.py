"""
Pydantic schemas for Recurring Transactions API
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

class TransaccionRecurrenteBase(BaseModel):
    id_cuenta: int
    id_cuenta_destino: Optional[int] = None
    id_beneficiario: int
    id_categoria: Optional[int] = None
    codigo_transaccion: str  # Withdrawal, Deposit, Transfer
    monto_transaccion: Decimal = Field(..., max_digits=20, decimal_places=8)
    notas: Optional[str] = None
    frecuencia: str  # Daily, Weekly, Bi-weekly, Monthly, Yearly, etc.
    intervalo: int = Field(default=1, ge=1)
    dia_semana: Optional[int] = Field(None, ge=0, le=6)
    dia_mes: Optional[int] = Field(None, ge=1, le=31)
    fecha_inicio: date
    proxima_fecha: date
    fecha_fin: Optional[date] = None
    limite_ejecuciones: int = Field(default=-1)
    activo: int = Field(1, ge=0, le=1)

class TransaccionRecurrenteCreate(TransaccionRecurrenteBase):
    pass

class TransaccionRecurrenteUpdate(BaseModel):
    id_cuenta: Optional[int] = None
    id_cuenta_destino: Optional[int] = None
    id_beneficiario: Optional[int] = None
    id_categoria: Optional[int] = None
    monto_transaccion: Optional[Decimal] = None
    notas: Optional[str] = None
    frecuencia: Optional[str] = None
    intervalo: Optional[int] = None
    dia_semana: Optional[int] = None
    dia_mes: Optional[int] = None
    proxima_fecha: Optional[date] = None
    fecha_fin: Optional[date] = None
    limite_ejecuciones: Optional[int] = None
    activo: Optional[int] = None

class TransaccionRecurrenteResponse(TransaccionRecurrenteBase):
    id_recurrencia: int
    ejecuciones_realizadas: int
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True

class ExecutionHistory(BaseModel):
    """Placeholder for execution history if needed later"""
    id_transaccion: int
    fecha_ejecucion: datetime
