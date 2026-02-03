"""
Advanced models for FuturoForbes 3F
Phase 2: Recurring Transactions, Assets, and Investments
"""
from datetime import date, datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from decimal import Decimal

# ==================== RECURRING TRANSACTIONS ====================

class TransaccionRecurrente(SQLModel, table=True):
    """
    Scheduled or recurring transactions that happen periodically.
    Inspired by MMEX Scheduled Transactions.
    """
    __tablename__ = "transacciones_programadas"
    
    id_recurrencia: Optional[int] = Field(default=None, primary_key=True)
    
    # Core transaction data
    id_cuenta: int = Field(foreign_key="lista_cuentas.id_cuenta")
    id_cuenta_destino: Optional[int] = Field(default=None, foreign_key="lista_cuentas.id_cuenta")
    id_beneficiario: int = Field(foreign_key="beneficiarios.id_beneficiario")
    id_categoria: Optional[int] = Field(default=None, foreign_key="categorias.id_categoria")
    
    codigo_transaccion: str  # Withdrawal, Deposit, Transfer
    monto_transaccion: Decimal = Field(max_digits=20, decimal_places=8)
    notas: Optional[str] = None
    
    # Recurring logic
    frecuencia: str  # Daily, Weekly, Bi-weekly, Monthly, Yearly, etc.
    intervalo: int = Field(default=1)  # Every 1 month, every 2 weeks, etc.
    
    dia_semana: Optional[int] = None  # 0-6 (Mon-Sun)
    dia_mes: Optional[int] = None     # 1-31
    
    fecha_inicio: date = Field(index=True)
    proxima_fecha: date = Field(index=True)
    fecha_fin: Optional[date] = None
    
    limite_ejecuciones: int = Field(default=-1)  # -1 for unlimited
    ejecuciones_realizadas: int = Field(default=0)
    
    activo: int = Field(default=1, index=True)
    fecha_creacion: Optional[datetime] = None  # MySQL auto-generated
    fecha_actualizacion: Optional[datetime] = None  # MySQL auto-updated


# ==================== ASSETS (ACTIVOS) ====================

class Activo(SQLModel, table=True):
    """
    Physical assets tracking (Property, Vehicles, Art, etc.)
    Inspired by MMEX Assets.
    """
    __tablename__ = "activos"
    
    id_activo: Optional[int] = Field(default=None, primary_key=True)
    nombre_activo: str = Field(max_length=255, index=True)
    tipo_activo: str  # Property, Automobile, Household, Art, Jewelry, etc.
    
    valor_inicial: Decimal = Field(max_digits=20, decimal_places=8)
    valor_actual: Decimal = Field(max_digits=20, decimal_places=8)
    
    fecha_compra: Optional[date] = None
    notas: Optional[str] = None
    
    # Depreciation / Appreciation logic
    tasa_variacion: Decimal = Field(default=0, max_digits=10, decimal_places=4) # % variation
    metodo_variacion: str = Field(default="None") # Linear, Percentage, None
    frecuencia_variacion: str = Field(default="Yearly") # Monthly, Yearly
    
    activo: int = Field(default=1, index=True)
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None


class HistorialActivo(SQLModel, table=True):
    """
    Tracks value changes of an asset over time.
    """
    __tablename__ = "historial_activos"
    
    id_historial: Optional[int] = Field(default=None, primary_key=True)
    id_activo: int = Field(foreign_key="activos.id_activo", ondelete="CASCADE")
    fecha: date = Field(index=True)
    valor: Decimal = Field(max_digits=20, decimal_places=8)
    notas: Optional[str] = None
    fecha_creacion: Optional[datetime] = None


# ==================== INVESTMENTS (INVERSIONES / STOCKS) ====================

class Inversion(SQLModel, table=True):
    """
    Stock/Investment holdings.
    Inspired by MMEX Stocks.
    """
    __tablename__ = "inversiones"
    
    id_inversion: Optional[int] = Field(default=None, primary_key=True)
    id_cuenta: int = Field(foreign_key="lista_cuentas.id_cuenta")
    
    nombre_inversion: str = Field(max_length=255, index=True)
    simbolo: str = Field(max_length=20, index=True) # Ticker (AAPL, BTC, etc.)
    tipo_inversion: str = Field(default="Stock") # Stock, Fund, Crypto, etc.
    
    cantidad: Decimal = Field(max_digits=20, decimal_places=8)
    precio_compra: Decimal = Field(max_digits=20, decimal_places=8)
    precio_actual: Decimal = Field(max_digits=20, decimal_places=8)
    
    comision: Decimal = Field(default=0, max_digits=20, decimal_places=8)
    notas: Optional[str] = None
    
    activo: int = Field(default=1, index=True)
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None


class HistorialInversion(SQLModel, table=True):
    """
    Historical price data for an investment.
    """
    __tablename__ = "historial_inversiones"
    
    id_historial: Optional[int] = Field(default=None, primary_key=True)
    id_inversion: int = Field(foreign_key="inversiones.id_inversion", ondelete="CASCADE")
    fecha: date = Field(index=True)
    precio: Decimal = Field(max_digits=20, decimal_places=8)
    
    fecha_creacion: Optional[datetime] = None


class TransaccionInversion(SQLModel, table=True):
    """
    Ledger for investment movements (Buy, Sell, Dividends, Splits).
    Provides history that doesn't exist in the summary 'Inversion' model.
    """
    __tablename__ = "transacciones_inversion"
    
    id_transaccion_inv: Optional[int] = Field(default=None, primary_key=True)
    id_inversion: int = Field(foreign_key="inversiones.id_inversion", ondelete="CASCADE")
    id_cuenta: int = Field(foreign_key="lista_cuentas.id_cuenta")
    
    tipo_operacion: str # Buy, Sell, Dividend, Reinvest, Split
    fecha: date = Field(index=True)
    
    cantidad: Decimal = Field(max_digits=20, decimal_places=8)
    precio_unitario: Decimal = Field(max_digits=20, decimal_places=8)
    comision: Decimal = Field(default=0, max_digits=20, decimal_places=8)
    impuestos: Decimal = Field(default=0, max_digits=20, decimal_places=8)
    total: Decimal = Field(max_digits=20, decimal_places=8)
    
    notas: Optional[str] = None
    fecha_creacion: Optional[datetime] = None
