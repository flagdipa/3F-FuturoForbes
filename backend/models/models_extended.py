"""
Extended models for MMEX-inspired features (Phase 1)
- Tags system for flexible classification
- Polymorphic attachments for documents
- Currency history for exchange rates
"""
from datetime import datetime, date
from typing import Optional
from sqlmodel import SQLModel, Field
from decimal import Decimal

# ==================== TAGS SYSTEM ====================

class Etiqueta(SQLModel, table=True):
    """
    Tags for flexible classification of transactions and other entities.
    Many-to-many relationship with transactions.
    """
    __tablename__ = "etiquetas"
    
    id_etiqueta: Optional[int] = Field(default=None, primary_key=True)
    nombre_etiqueta: str = Field(unique=True, max_length=100, index=True)
    color: Optional[str] = Field(default=None, max_length=7)  # Hex color #RRGGBB
    activo: int = Field(default=1)


class TransaccionEtiqueta(SQLModel, table=True):
    """
    Many-to-many relationship between transactions and tags.
    Allows tagging transactions for flexible filtering and reporting.
    """
    __tablename__ = "transacciones_etiquetas"
    
    id_transaccion: int = Field(
        foreign_key="libro_transacciones.id_transaccion",
        primary_key=True,
        ondelete="CASCADE"
    )
    id_etiqueta: int = Field(
        foreign_key="etiquetas.id_etiqueta",
        primary_key=True,
        ondelete="CASCADE"
    )


# ==================== ATTACHMENTS ====================

class Adjunto(SQLModel, table=True):
    """
    Polymorphic attachments for any entity type.
    Stores files (receipts, contracts, invoices) linked to transactions, accounts, etc.
    
    tipo_referencia examples: 'Transaccion', 'Cuenta', 'Beneficiario', 'Activo'
    """
    __tablename__ = "adjuntos"
    
    id_adjunto: Optional[int] = Field(default=None, primary_key=True)
    tipo_referencia: str = Field(max_length=50, index=True)  # Entity type
    id_referencia: int = Field(index=True)  # Entity ID
    descripcion: Optional[str] = None
    nombre_archivo: str = Field(max_length=255)
    ruta_archivo: str  # Full path or cloud storage URL
    tipo_mime: Optional[str] = Field(default=None, max_length=100)
    tamaño_bytes: Optional[int] = None
    fecha_creacion: Optional[datetime] = None  # MySQL auto-generates this
    fecha_actualizacion: Optional[datetime] = None  # MySQL auto-updates this


# ==================== CURRENCY HISTORY ====================

class HistorialDivisa(SQLModel, table=True):
    """
    Historical exchange rates for currencies.
    Enables accurate conversion for past transactions.
    """
    __tablename__ = "historial_divisas"
    
    id_historial: Optional[int] = Field(default=None, primary_key=True)
    id_divisa: int = Field(foreign_key="divisas.id_divisa", index=True)
    fecha_tasa: date = Field(index=True)
    tasa_valor: Decimal = Field(max_digits=20, decimal_places=8)
    tipo_actualizacion: int = Field(default=0)  # 0=Manual, 1=Automatic
    fecha_creacion: Optional[datetime] = None  # MySQL auto-generates this
    
    class Config:
        # Unique constraint on (id_divisa, fecha_tasa)
        indexes = [
            ("id_divisa", "fecha_tasa")
        ]


# ==================== IMPORT RULES (REGLAS DE IMPORTACIÓN) ====================

class ReglaImportacion(SQLModel, table=True):
    """
    Rules for auto-categorizing transactions during CSV bank import.
    When a CSV description matches 'patron', the rule suggests a category and/or beneficiary.
    Rules are evaluated by priority (higher = first) and only active rules apply.
    """
    __tablename__ = "reglas_importacion"

    id_regla: Optional[int] = Field(default=None, primary_key=True)
    id_usuario: int = Field(foreign_key="usuarios.id_usuario", index=True)
    patron: str = Field(max_length=255)  # Substring or regex pattern to match CSV descriptions
    id_categoria: Optional[int] = Field(default=None, foreign_key="categorias.id_categoria")
    id_beneficiario: Optional[int] = Field(default=None, foreign_key="beneficiarios.id_beneficiario")
    prioridad: int = Field(default=0)  # Higher = evaluated first
    activo: int = Field(default=1)

