"""
Schemas for Financial Entities (Types and Institutions)
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List


# --- Tipo Entidad Financiera ---

class TipoEntidadBase(BaseModel):
    nombre_tipo: str
    descripcion: Optional[str] = None
    icono: str = "fa-university"
    color: str = "#0d6efd"
    activo: bool = True


class TipoEntidadCreate(TipoEntidadBase):
    pass


class TipoEntidadUpdate(BaseModel):
    nombre_tipo: Optional[str] = None
    descripcion: Optional[str] = None
    icono: Optional[str] = None
    color: Optional[str] = None
    activo: Optional[bool] = None


class TipoEntidadResponse(TipoEntidadBase):
    id_tipo: int
    
    model_config = ConfigDict(from_attributes=True)


# --- Identidad Financiera (Entidad específica) ---

class IdentidadFinancieraBase(BaseModel):
    nombre: str
    id_tipo: Optional[int] = None
    sucursal: Optional[str] = None
    direccion: Optional[str] = None
    web: Optional[str] = None
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    cuit: Optional[str] = None
    logo_url: Optional[str] = None
    activo: bool = True


class IdentidadFinancieraCreate(IdentidadFinancieraBase):
    pass


class IdentidadFinancieraUpdate(BaseModel):
    nombre: Optional[str] = None
    id_tipo: Optional[int] = None
    sucursal: Optional[str] = None
    direccion: Optional[str] = None
    web: Optional[str] = None
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    cuit: Optional[str] = None
    logo_url: Optional[str] = None
    activo: Optional[bool] = None


class IdentidadFinancieraResponse(IdentidadFinancieraBase):
    id_identidad: int
    tipo_nombre: Optional[str] = None  # Populated from join
    tipo_icono: Optional[str] = None
    tipo_color: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# --- Response with nested data ---

class TipoEntidadConEntidades(TipoEntidadResponse):
    """Tipo with list of entities"""
    entidades: List[IdentidadFinancieraResponse] = []
