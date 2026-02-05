from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class AnioPresupuestoBase(BaseModel):
    anio: int
    nombre: str
    notas: Optional[str] = None
    activo: Optional[int] = 1

class AnioPresupuestoCreate(AnioPresupuestoBase):
    pass

class AnioPresupuestoUpdate(BaseModel):
    anio: Optional[int] = None
    nombre: Optional[str] = None
    notas: Optional[str] = None
    activo: Optional[int] = None

class AnioPresupuestoResponse(AnioPresupuestoBase):
    id_anio_presupuesto: int
