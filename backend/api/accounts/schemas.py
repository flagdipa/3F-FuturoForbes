from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class CuentaBase(BaseModel):
    nombre_cuenta: str
    tipo_cuenta: str
    numero_cuenta: Optional[str] = None
    estado: str = "Open"
    notas: Optional[str] = None
    id_identidad_financiera: Optional[int] = None
    sitio_web: Optional[str] = None
    saldo_inicial: Optional[Decimal] = 0.00
    cuenta_favorita: int = 0
    id_divisa: int
    saldo_minimo: Optional[Decimal] = 0.00
    limite_credito: Optional[Decimal] = 0.00
    tasa_interes: Optional[Decimal] = 0.00

class CuentaCrear(CuentaBase): # Renombrado
    pass

class CuentaLectura(CuentaBase): # Renombrado
    id_cuenta: int
    identidad_financiera: Optional["IdentidadFinancieraResponse"] = None

    class Config:
        from_attributes = True

from ..financial_entities.schemas import IdentidadFinancieraResponse
CuentaLectura.model_rebuild()
