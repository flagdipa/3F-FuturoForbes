"""
Advanced schemas for Budget API (Phase 3)
Includes Multi-Year Budget Setup
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class AñoPresupuestoBase(BaseModel):
    anio: int = Field(..., description="Year e.g. 2024, 2025")
    nombre: str = Field(..., max_length=100)
    notas: Optional[str] = None
    activo: int = Field(1, ge=0, le=1)

class AñoPresupuestoCreate(AñoPresupuestoBase):
    pass

class AñoPresupuestoUpdate(BaseModel):
    anio: Optional[int] = None
    nombre: Optional[str] = None
    notas: Optional[str] = None
    activo: Optional[int] = None

class AñoPresupuestoResponse(AñoPresupuestoBase):
    id_anio_presupuesto: int
    fecha_creacion: Optional[datetime] = None

    class Config:
        from_attributes = True
