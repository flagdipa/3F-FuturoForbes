"""
Pydantic schemas for Custom Fields (EAV) API
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

# ==================== FIELD DEFINITIONS ====================

class CampoPersonalizadoBase(BaseModel):
    nombre_campo: str = Field(..., max_length=100)
    tipo_entidad: str = Field(..., description="Target entity type: Transaccion, Cuenta, Beneficiario")
    tipo_dato: str = Field(..., description="Data type: String, Number, Date, Boolean")
    requerido: bool = Field(False)
    activo: int = Field(1, ge=0, le=1)

class CampoPersonalizadoCreate(CampoPersonalizadoBase):
    pass

class CampoPersonalizadoUpdate(BaseModel):
    nombre_campo: Optional[str] = None
    tipo_dato: Optional[str] = None
    requerido: Optional[bool] = None
    activo: Optional[int] = None

class CampoPersonalizadoResponse(CampoPersonalizadoBase):
    id_campo: int

    class Config:
        from_attributes = True

# ==================== FIELD VALUES ====================

class ValorCampoPersonalizadoBase(BaseModel):
    id_campo: int
    id_entidad: int
    valor: str

class ValorCampoPersonalizadoCreate(ValorCampoPersonalizadoBase):
    pass

class ValorCampoPersonalizadoResponse(ValorCampoPersonalizadoBase):
    id_valor: int
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True

# ==================== BULK OPERATIONS ====================

class EntityCustomFieldValue(BaseModel):
    id_campo: int
    valor: str

class EntityCustomFieldsUpdate(BaseModel):
    values: List[EntityCustomFieldValue]
