from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

class TransaccionBase(BaseModel):
    id_cuenta: int
    id_cuenta_destino: Optional[int] = None
    id_beneficiario: int
    codigo_transaccion: str
    monto_transaccion: Decimal
    estado: Optional[str] = "None"
    numero_transaccion: Optional[str] = None
    notas: Optional[str] = None
    id_categoria: Optional[int] = None
    fecha_transaccion: Optional[str] = None
    etiquetas: List[int] = []
    monto_cuenta_destino: Optional[Decimal] = None
    color: int = -1
    es_dividida: bool = False

class TransaccionCrear(BaseModel):
    id_cuenta: int
    id_cuenta_destino: Optional[int] = None
    id_beneficiario: int
    codigo_transaccion: str
    monto_transaccion: Decimal
    estado: Optional[str] = "None"
    numero_transaccion: Optional[str] = None
    notas: Optional[str] = None
    id_categoria: Optional[int] = None
    fecha_transaccion: Optional[str] = None
    etiquetas: List[int] = []
    monto_cuenta_destino: Optional[Decimal] = None
    color: int = -1
    es_dividida: bool = False

class TransaccionLectura(TransaccionBase):
    id_transaccion: int
    fecha_actualizacion: Optional[str] = None
    nombre_cuenta: Optional[str] = None # Campo extra
    nombre_beneficiario: Optional[str] = None # Campo extra
    nombre_categoria: Optional[str] = None # Campo extra
    saldo: Optional[Decimal] = None # Running balance

    class Config:
        from_attributes = True

class DivisionCrear(BaseModel):
    id_categoria: Optional[int] = None
    monto_division: Decimal
    notas: Optional[str] = None

class TransaccionComplejaCrear(TransaccionCrear):
    divisiones: List[DivisionCrear] = []
