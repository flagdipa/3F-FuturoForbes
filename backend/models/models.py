from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from decimal import Decimal

# --- SEGURIDAD Y USUARIOS ---

class Usuario(SQLModel, table=True):
    __tablename__ = "usuarios"
    id_usuario: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password: str
    creado_el: datetime = Field(default_factory=datetime.utcnow)
    actualizado_el: datetime = Field(default_factory=datetime.utcnow)
    bloqueado: bool = Field(default=False)
    rol_id: Optional[int] = None

# --- CATÁLOGOS ---

class Divisa(SQLModel, table=True):
    __tablename__ = "divisas"
    id_divisa: Optional[int] = Field(default=None, primary_key=True)
    nombre_divisa: str = Field(unique=True)
    codigo_iso: str = Field(unique=True)
    simbolo_prefijo: Optional[str] = None
    simbolo_sufijo: Optional[str] = None
    punto_decimal: Optional[str] = None
    separador_grupo: Optional[str] = None
    nombre_unidad: Optional[str] = None
    nombre_centavo: Optional[str] = None
    escala: Optional[int] = None
    tasa_conversion_base: Optional[Decimal] = Field(default=None, max_digits=20, decimal_places=8)
    tipo_divisa: str # Fiat o Crypto
    decimal_places: int = Field(default=2)

class IdentidadFinanciera(SQLModel, table=True):
    __tablename__ = "identidades_financieras"
    id_identidad: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True)
    tipo: Optional[str] = None
    sucursal: Optional[str] = None
    direccion: Optional[str] = None
    web: Optional[str] = None
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    cuit: Optional[Decimal] = None

# --- CLASIFICACIÓN ---

class Categoria(SQLModel, table=True):
    __tablename__ = "categorias"
    id_categoria: Optional[int] = Field(default=None, primary_key=True)
    nombre_categoria: str
    activo: int = Field(default=1)
    id_padre: Optional[int] = Field(default=None, foreign_key="categorias.id_categoria")
    color: Optional[str] = None
    notas: Optional[str] = None

class Beneficiario(SQLModel, table=True):
    __tablename__ = "beneficiarios"
    id_beneficiario: Optional[int] = Field(default=None, primary_key=True)
    nombre_beneficiario: str = Field(unique=True)
    id_categoria: Optional[int] = Field(default=None, foreign_key="categorias.id_categoria")
    cbu: Optional[str] = None
    numero: Optional[str] = None
    sitio_web: Optional[str] = None
    notas: Optional[str] = None
    activo: int = Field(default=1)
    patron_busqueda: Optional[str] = None
    cuit: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    oculto: int = Field(default=0)
    banco: Optional[str] = None

# --- CUENTAS ---

class ListaCuentas(SQLModel, table=True):
    __tablename__ = "lista_cuentas"
    id_cuenta: Optional[int] = Field(default=None, primary_key=True)
    nombre_cuenta: str = Field(unique=True)
    tipo_cuenta: str
    numero_cuenta: Optional[str] = None
    estado: str = Field(default="Open") # Open, Closed
    notas: Optional[str] = None
    entidad_financiera: Optional[str] = None
    sitio_web: Optional[str] = None
    info_contacto: Optional[str] = None
    info_acceso: Optional[str] = None
    saldo_inicial: Decimal = Field(default=0.00, max_digits=15, decimal_places=2)
    cuenta_favorita: int = Field(default=0)
    id_divisa: int = Field(foreign_key="divisas.id_divisa")
    extracto_bloqueado: int = Field(default=0)
    fecha_extracto: Optional[str] = None
    saldo_minimo: Decimal = Field(default=0.00, max_digits=15, decimal_places=2)
    limite_credito: Decimal = Field(default=0.00, max_digits=15, decimal_places=2)
    tasa_interes: Decimal = Field(default=0.00, max_digits=15, decimal_places=2)
    fecha_vencimiento_pago: Optional[str] = None
    pago_minimo: Decimal = Field(default=0.00, max_digits=15, decimal_places=2)
    fecha_inicial: Optional[str] = None

# --- TRANSACCIONES ---

class LibroTransacciones(SQLModel, table=True):
    __tablename__ = "libro_transacciones"
    id_transaccion: Optional[int] = Field(default=None, primary_key=True)
    id_cuenta: int = Field(foreign_key="lista_cuentas.id_cuenta")
    id_cuenta_destino: Optional[int] = Field(default=None, foreign_key="lista_cuentas.id_cuenta")
    id_beneficiario: int = Field(foreign_key="beneficiarios.id_beneficiario")
    codigo_transaccion: str # Withdrawal, Deposit, Transfer
    monto_transaccion: Decimal = Field(max_digits=20, decimal_places=8)
    estado: Optional[str] = None
    numero_transaccion: Optional[str] = None
    notas: Optional[str] = None
    id_categoria: Optional[int] = Field(default=None, foreign_key="categorias.id_categoria")
    fecha_transaccion: Optional[str] = None
    fecha_actualizacion: Optional[str] = None
    fecha_eliminacion: Optional[str] = None
    id_seguimiento: Optional[int] = None
    monto_cuenta_destino: Optional[Decimal] = Field(default=None, max_digits=20, decimal_places=8)
    color: int = Field(default=-1)
    es_dividida: bool = Field(default=False)

class TransaccionDividida(SQLModel, table=True):
    __tablename__ = "transacciones_divididas"
    id_division: Optional[int] = Field(default=None, primary_key=True)
    id_transaccion: int = Field(foreign_key="libro_transacciones.id_transaccion")
    id_categoria: Optional[int] = Field(default=None, foreign_key="categorias.id_categoria")
    monto_division: Decimal = Field(max_digits=20, decimal_places=8)
    notas: Optional[str] = None

# --- PRESUPUESTOS ---

class Presupuesto(SQLModel, table=True):
    __tablename__ = "tabla_presupuestos"
    id_presupuesto: Optional[int] = Field(default=None, primary_key=True)
    id_anio_presupuesto: Optional[int] = Field(
        default=None, 
        foreign_key="anios_presupuesto.id_anio_presupuesto",
        ondelete="SET NULL"
    )
    id_categoria: int = Field(foreign_key="categorias.id_categoria")
    periodo: str = Field(default="Monthly")
    monto: Decimal = Field(default=0.00, max_digits=15, decimal_places=2)
    notas: Optional[str] = None
    activo: int = Field(default=1)
