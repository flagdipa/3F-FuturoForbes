from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class DivisaBase(BaseModel):
    nombre_divisa: str
    codigo_iso: str
    simbolo_prefijo: Optional[str] = None
    simbolo_sufijo: Optional[str] = None
    punto_decimal: Optional[str] = "."
    separador_grupo: Optional[str] = ","
    escala: Optional[int] = 2
    tasa_conversion_base: Optional[Decimal] = None
    tipo_divisa: str # Fiat o Crypto

class DivisaCrear(DivisaBase): # Renombrado
    pass

class DivisaLectura(DivisaBase): # Renombrado
    id_divisa: int

    class Config:
        from_attributes = True
