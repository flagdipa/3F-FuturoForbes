from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from decimal import Decimal

# --- SEGURIDAD Y USUARIOS ---

class Usuario(SQLModel, table=True):
    """
    Application user account. Stores credentials, role, and personal preferences.
    """
    __tablename__ = "usuarios"
    id_usuario: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password: str
    creado_el: datetime = Field(default_factory=datetime.utcnow)
    actualizado_el: datetime = Field(default_factory=datetime.utcnow)
    bloqueado: bool = Field(default=False)
    rol_id: Optional[int] = None
    theme_preference: str = Field(default="dark_neon")  # Theme ID
    nombre: Optional[str] = Field(default=None, max_length=100)
    apellido: Optional[str] = Field(default=None, max_length=100)

# --- CATÁLOGOS ---

class Divisa(SQLModel, table=True):
    """
    Currency definition (Fiat or Crypto).
    Stores formatting rules and conversion rates.
    """
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

class TipoEntidadFinanciera(SQLModel, table=True):
    """
    Type classification for financial entities.
    Examples: Banco, Broker, Fintech, Billetera Virtual, Cooperativa, Caja de Ahorro
    """
    __tablename__ = "tipos_entidad_financiera"
    id_tipo: Optional[int] = Field(default=None, primary_key=True)
    nombre_tipo: str = Field(unique=True)  # Banco, Broker, Fintech, etc.
    descripcion: Optional[str] = None
    icono: str = Field(default="fa-university")  # FontAwesome icon
    color: str = Field(default="#0d6efd")  # Hex color for UI
    activo: bool = Field(default=True)
    
    # Relationship
    entidades: List["IdentidadFinanciera"] = Relationship(back_populates="tipo_entidad")

class IdentidadFinanciera(SQLModel, table=True):
    """
    Specific financial institution (e.g., Santander, Balanz, Mercado Pago).
    Linked to a type and can be associated with accounts.
    """
    __tablename__ = "identidades_financieras"
    id_identidad: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True)
    id_tipo: Optional[int] = Field(default=None, foreign_key="tipos_entidad_financiera.id_tipo")
    sucursal: Optional[str] = None
    direccion: Optional[str] = None
    web: Optional[str] = None
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    cuit: Optional[str] = None
    logo_url: Optional[str] = None  # URL or path to logo
    activo: bool = Field(default=True)
    
    # Relationships
    tipo_entidad: Optional["TipoEntidadFinanciera"] = Relationship(back_populates="entidades")
    cuentas: List["ListaCuentas"] = Relationship(back_populates="identidad_financiera")


# --- CLASIFICACIÓN ---

class Categoria(SQLModel, table=True):
    """
    Classification category for transactions (e.g., Food, Rent, Salary).
    Supports hierarchical structure via id_padre.
    """
    __tablename__ = "categorias"
    id_categoria: Optional[int] = Field(default=None, primary_key=True)
    nombre_categoria: str
    activo: int = Field(default=1)
    id_padre: Optional[int] = Field(default=None, foreign_key="categorias.id_categoria")
    color: Optional[str] = None
    notas: Optional[str] = None
    
    # Relationships
    transacciones: List["LibroTransacciones"] = Relationship(back_populates="categoria")

class Beneficiario(SQLModel, table=True):
    """
    Payee or recipient of a transaction.
    Stores banking info (CBU/CUIT) and default category for auto-tagging.
    """
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
    
    # Relationships
    transacciones: List["LibroTransacciones"] = Relationship(back_populates="beneficiario")

# --- CUENTAS ---

class ListaCuentas(SQLModel, table=True):
    """
    Financial account (Bank, Cash, Crypto Wallet).
    Tracks balances, limits, and interest rates if applicable.
    """
    __tablename__ = "lista_cuentas"
    id_cuenta: Optional[int] = Field(default=None, primary_key=True)
    nombre_cuenta: str = Field(unique=True)
    tipo_cuenta: str
    numero_cuenta: Optional[str] = None
    estado: str = Field(default="Open") # Open, Closed
    notas: Optional[str] = None
    id_identidad_financiera: Optional[int] = Field(default=None, foreign_key="identidades_financieras.id_identidad")
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
    
    # Relationships
    identidad_financiera: Optional["IdentidadFinanciera"] = Relationship(back_populates="cuentas")
    divisa: Optional["Divisa"] = Relationship()
    transacciones: List["LibroTransacciones"] = Relationship(
        back_populates="cuenta",
        sa_relationship_kwargs={"primaryjoin": "LibroTransacciones.id_cuenta == ListaCuentas.id_cuenta"}
    )

# --- TRANSACCIONES ---

class LibroTransacciones(SQLModel, table=True):
    """
    Core ledger entry. Represents any monetary movement (Income, Expense, Transfer).
    Can be linked to splits and tags.
    """
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
    
    # Relationships
    cuenta: "ListaCuentas" = Relationship(
        back_populates="transacciones",
        sa_relationship_kwargs={"primaryjoin": "LibroTransacciones.id_cuenta == ListaCuentas.id_cuenta"}
    )
    beneficiario: "Beneficiario" = Relationship(back_populates="transacciones")
    categoria: "Categoria" = Relationship(back_populates="transacciones")

class TransaccionDividida(SQLModel, table=True):
    """
    A single part of a split transaction.
    Multiple splits must sum up to the parent transaction total.
    """
    __tablename__ = "transacciones_divididas"
    id_division: Optional[int] = Field(default=None, primary_key=True)
    id_transaccion: int = Field(foreign_key="libro_transacciones.id_transaccion")
    id_categoria: Optional[int] = Field(default=None, foreign_key="categorias.id_categoria")
    monto_division: Decimal = Field(max_digits=20, decimal_places=8)
    notas: Optional[str] = None

# --- PRESUPUESTOS ---

class Presupuesto(SQLModel, table=True):
    """
    Budget allocation for a specific category and year/period.
    """
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
    
    # Phase 14: Rolling Budgets
    es_rolling: bool = Field(default=False) 
    monto_acumulado: Decimal = Field(default=0, max_digits=15, decimal_places=2)

# -----------------------------------------------------------------------------
# MODELO: METAS DE AHORRO (Saving Goals)
# -----------------------------------------------------------------------------
class MetaAhorro(SQLModel, table=True):
    __tablename__ = "metas_ahorro"

    id_meta: Optional[int] = Field(default=None, primary_key=True)
    id_usuario: int = Field(foreign_key="usuarios.id_usuario")
    id_cuenta: Optional[int] = Field(default=None, foreign_key="lista_cuentas.id_cuenta")
    nombre_meta: str
    monto_objetivo: Decimal = Field(default=0, max_digits=20, decimal_places=2)
    monto_actual: Decimal = Field(default=0, max_digits=20, decimal_places=2)
    fecha_limite: Optional[str] = None # ISO format YYYY-MM-DD
    color: str = Field(default="#0d6efd") # Hex color for UI
    icono: str = Field(default="fa-bullseye") # FontAwesome icon class
    notas: Optional[str] = None
    estado: str = Field(default="ACTIVA") # ACTIVA, COMPLETADA, PAUSADA
    
    fecha_creacion: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    fecha_actualizacion: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
