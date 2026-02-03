from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class CuentaBase(BaseModel):
    nombre_cuenta: str
    tipo_cuenta: str
    numero_cuenta: Optional[str] = None
    estado: str = "Open"
    notas: Optional[str] = None
    entidad_financiera: Optional[str] = None
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

    class Config:
        from_attributes = True
