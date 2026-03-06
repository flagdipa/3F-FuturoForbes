"""
Modelos de base de datos — Plugin Cuentas / Billetera
Gestión de tasas de interés de wallets y fintechs argentinas.
"""
from typing import Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Numeric, Text


class TipoTasa(str, Enum):
    TNA = "TNA"   # Tasa Nominal Anual
    TEA = "TEA"   # Tasa Efectiva Anual
    TEM = "TEM"   # Tasa Efectiva Mensual
    VARIABLE = "Variable"


class MonedaTasa(str, Enum):
    ARS = "ARS"
    USDT = "USDT"
    DAI = "DAI"
    USD = "USD"
    BTC = "BTC"


class FuenteDato(str, Enum):
    MANUAL = "Manual"
    API = "API"
    SCRAPING = "Scraping"


# ── Tabla de wallets/fintechs ────────────────────────────────────────────────

class CuentasWalletEntidad(SQLModel, table=True):
    __tablename__ = "cuentaswallet_entidades"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, max_length=120)
    nombre_corto: str = Field(default="", max_length=40)
    tipo: str = Field(default="Fintech", max_length=60)
    # Tipos: Banco, Fintech, Billetera Virtual, Exchange Crypto
    url_web: Optional[str] = Field(default=None, max_length=255)
    url_logo: Optional[str] = Field(default=None, max_length=255)
    color_hex: str = Field(default="#6c757d", max_length=7)
    descripcion: Optional[str] = Field(default=None, sa_column=Column(Text))
    activa: bool = Field(default=True)
    creado_el: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Mercado Pago",
                "nombre_corto": "MP",
                "tipo": "Billetera Virtual",
                "color_hex": "#009EE3",
            }
        }


# ── Tabla de tasas actuales ──────────────────────────────────────────────────

class CuentasWalletTasa(SQLModel, table=True):
    __tablename__ = "cuentaswallet_tasas"

    id: Optional[int] = Field(default=None, primary_key=True)
    id_entidad: int = Field(foreign_key="cuentaswallet_entidades.id", index=True)
    tipo_producto: str = Field(
        default="Cuenta Remunerada", max_length=80
    )
    # Tipos producto: Cuenta Remunerada, Plazo Fijo, FCI, Crypto Yield
    tipo_tasa: TipoTasa = Field(default=TipoTasa.TNA)
    moneda: MonedaTasa = Field(default=MonedaTasa.ARS)
    valor: Decimal = Field(
        default=Decimal("0"), sa_column=Column(Numeric(precision=10, scale=4))
    )
    valor_tea: Optional[Decimal] = Field(
        default=None, sa_column=Column(Numeric(precision=10, scale=4))
    )
    plazo_dias: Optional[int] = Field(default=None)
    monto_minimo: Optional[Decimal] = Field(
        default=None, sa_column=Column(Numeric(precision=19, scale=2))
    )
    condiciones: Optional[str] = Field(default=None, sa_column=Column(Text))
    fuente: FuenteDato = Field(default=FuenteDato.MANUAL)
    url_fuente: Optional[str] = Field(default=None, max_length=255)
    fecha_vigencia: Optional[datetime] = Field(default=None)
    actualizado_el: datetime = Field(default_factory=datetime.utcnow)
    activa: bool = Field(default=True)


# ── Historial de tasas ───────────────────────────────────────────────────────

class CuentasWalletHistorial(SQLModel, table=True):
    __tablename__ = "cuentaswallet_historial"

    id: Optional[int] = Field(default=None, primary_key=True)
    id_tasa: int = Field(foreign_key="cuentaswallet_tasas.id", index=True)
    id_entidad: int = Field(index=True)
    tipo_producto: str = Field(max_length=80)
    moneda: str = Field(max_length=10)
    valor_anterior: Decimal = Field(
        sa_column=Column(Numeric(precision=10, scale=4))
    )
    valor_nuevo: Decimal = Field(
        sa_column=Column(Numeric(precision=10, scale=4))
    )
    variacion: Decimal = Field(
        default=Decimal("0"), sa_column=Column(Numeric(precision=10, scale=4))
    )
    registrado_el: datetime = Field(default_factory=datetime.utcnow)
    fuente: FuenteDato = Field(default=FuenteDato.MANUAL)
