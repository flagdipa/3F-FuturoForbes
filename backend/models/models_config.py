"""
Configuration and metadata models for FuturoForbes 3F
Phase 3: Budget Years, System Settings, and Custom Fields (EAV)
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from decimal import Decimal

# ==================== BUDGET YEARS (AÑOS DE PRESUPUESTO) ====================

class AnioPresupuesto(SQLModel, table=True):
    """
    Groups budget entries by year.
    Allows for historical budget analysis and planning.
    """
    __tablename__ = "anios_presupuesto"
    
    id_anio_presupuesto: Optional[int] = Field(default=None, primary_key=True)
    anio: int = Field(unique=True, index=True) # e.g. 2024, 2025
    nombre: str = Field(max_length=100) # e.g. "Presupuesto anual 2024"
    notas: Optional[str] = None
    
    activo: int = Field(default=1, index=True) # 1 = Current/Active, 0 = Archived
    fecha_creacion: Optional[datetime] = None


# ==================== SYSTEM CONFIGURATION ====================

class Configuracion(SQLModel, table=True):
    """
    Key-Value storage for system-wide settings.
    """
    __tablename__ = "configuraciones"
    
    clave: str = Field(primary_key=True, max_length=100)
    valor: str = Field(max_length=255)
    descripcion: Optional[str] = None
    fecha_actualizacion: Optional[datetime] = None


# ==================== CUSTOM FIELDS (EAV PATTERN) ====================

class CampoPersonalizado(SQLModel, table=True):
    """
    Definition of user-defined extra fields.
    """
    __tablename__ = "campos_personalizados"
    
    id_campo: Optional[int] = Field(default=None, primary_key=True)
    nombre_campo: str = Field(max_length=100)
    tipo_entidad: str # Transaccion, Cuenta, Beneficiario
    tipo_dato: str # String, Number, Date, Boolean
    requerido: bool = Field(default=False)
    activo: int = Field(default=1)


class ValorCampoPersonalizado(SQLModel, table=True):
    """
    Values for user-defined extra fields.
    """
    __tablename__ = "valores_campos_personalizados"
    
    id_valor: Optional[int] = Field(default=None, primary_key=True)
    id_campo: int = Field(foreign_key="campos_personalizados.id_campo", ondelete="CASCADE")
    id_entidad: int # Generic ID (depends on tipo_entidad)
    valor: str # Stored as string, casted in business logic
    
    fecha_actualizacion: Optional[datetime] = None
