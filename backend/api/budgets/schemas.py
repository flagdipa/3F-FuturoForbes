from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal

class PresupuestoBase(BaseModel):
    id_anio_presupuesto: Optional[int] = None
    id_categoria: int
    periodo: str = "Monthly"
    monto: Decimal = 0.00
    notas: Optional[str] = None
    activo: int = 1

class PresupuestoCrear(PresupuestoBase):
    pass

class PresupuestoLectura(PresupuestoBase):
    id_presupuesto: int
    nombre_categoria: Optional[str] = None
    gasto_actual: Decimal = 0.00
    porcentaje: float = 0.0

    class Config:
        from_attributes = True
