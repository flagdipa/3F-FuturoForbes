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
    info_contacto: Optional[str] = None
    info_acceso: Optional[str] = None
    saldo_inicial: Optional[Decimal] = 0.00
    cuenta_favorita: int = 0
    id_divisa: int
    extracto_bloqueado: int = 0
    fecha_extracto: Optional[str] = None
    saldo_minimo: Optional[Decimal] = 0.00
    limite_credito: Optional[Decimal] = 0.00
    tasa_interes: Optional[Decimal] = 0.00
    fecha_vencimiento_pago: Optional[str] = None
    pago_minimo: Optional[Decimal] = 0.00
    fecha_inicial: Optional[str] = None

class CuentaCrear(CuentaBase): 
    pass

class CuentaUpdate(CuentaBase):
    nombre_cuenta: Optional[str] = None
    tipo_cuenta: Optional[str] = None
    id_divisa: Optional[int] = None

class CuentaLectura(CuentaBase): 
    id_cuenta: int
    identidad_financiera: Optional["IdentidadFinancieraResponse"] = None
    divisa: Optional["DivisaLectura"] = None

    class Config:
        from_attributes = True

from ..financial_entities.schemas import IdentidadFinancieraResponse
from .schemas_divisa import DivisaLectura
CuentaLectura.model_rebuild()
