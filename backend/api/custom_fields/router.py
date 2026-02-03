"""
API Router for Custom Fields (EAV Pattern)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from ...core.database import get_session
from ...models.models_config import CampoPersonalizado, ValorCampoPersonalizado
from .schemas import (
    CampoPersonalizadoCreate, CampoPersonalizadoUpdate, CampoPersonalizadoResponse,
    ValorCampoPersonalizadoCreate, ValorCampoPersonalizadoResponse,
    EntityCustomFieldsUpdate
)

router = APIRouter(prefix="/custom-fields", tags=["Custom Fields"])

# ==================== FIELD DEFINITIONS CRUD ====================

@router.get("/definitions", response_model=List[CampoPersonalizadoResponse])
def list_field_definitions(
    tipo_entidad: Optional[str] = None,
    activo: Optional[int] = None,
    session: Session = Depends(get_session)
):
    """List all user-defined custom fields"""
    query = select(CampoPersonalizado)
    if tipo_entidad:
        query = query.where(CampoPersonalizado.tipo_entidad == tipo_entidad)
    if activo is not None:
        query = query.where(CampoPersonalizado.activo == activo)
    
    return session.exec(query).all()

@router.post("/definitions", response_model=CampoPersonalizadoResponse, status_code=status.HTTP_201_CREATED)
def create_field_definition(data: CampoPersonalizadoCreate, session: Session = Depends(get_session)):
    """Define a new custom field for an entity type"""
    field = CampoPersonalizado(**data.dict())
    session.add(field)
    session.commit()
    session.refresh(field)
    return field

@router.put("/definitions/{id_campo}", response_model=CampoPersonalizadoResponse)
def update_field_definition(
    id_campo: int, 
    data: CampoPersonalizadoUpdate, 
    session: Session = Depends(get_session)
):
    """Update custom field metadata"""
    field = session.get(CampoPersonalizado, id_campo)
    if not field:
        raise HTTPException(status_code=404, detail="Definición de campo no encontrada")
        
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(field, key, value)
        
    session.add(field)
    session.commit()
    session.refresh(field)
    return field

# ==================== VALUES MANAGEMENT ====================

@router.get("/values/{tipo_entidad}/{id_entidad}", response_model=List[ValorCampoPersonalizadoResponse])
def get_entity_values(tipo_entidad: str, id_entidad: int, session: Session = Depends(get_session)):
    """Get all custom field values for a specific entity record"""
    # Note: tipo_entidad is technically in the definition, but filtering by ID is primary
    query = select(ValorCampoPersonalizado).join(CampoPersonalizado).where(
        CampoPersonalizado.tipo_entidad == tipo_entidad,
        ValorCampoPersonalizado.id_entidad == id_entidad
    )
    return session.exec(query).all()

@router.post("/values", response_model=ValorCampoPersonalizadoResponse, status_code=status.HTTP_201_CREATED)
def set_field_value(data: ValorCampoPersonalizadoCreate, session: Session = Depends(get_session)):
    """Set or update a single field value for an entity"""
    # Verify field exists and matches entity type? (Omitted for brevity, but recommended)
    
    # Upsert logic
    existing = session.exec(select(ValorCampoPersonalizado).where(
        ValorCampoPersonalizado.id_campo == data.id_campo,
        ValorCampoPersonalizado.id_entidad == data.id_entidad
    )).first()
    
    if existing:
        existing.valor = data.valor
        existing.fecha_actualizacion = datetime.utcnow()
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing
    
    val = ValorCampoPersonalizado(**data.dict())
    val.fecha_actualizacion = datetime.utcnow()
    session.add(val)
    session.commit()
    session.refresh(val)
    return val

@router.post("/values/{tipo_entidad}/{id_entidad}/bulk")
def update_entity_bulk(
    tipo_entidad: str, 
    id_entidad: int, 
    data: EntityCustomFieldsUpdate, 
    session: Session = Depends(get_session)
):
    """Bulk update multiple custom fields for an entity"""
    results = []
    for item in data.values:
        # Check if exists
        existing = session.exec(select(ValorCampoPersonalizado).where(
            ValorCampoPersonalizado.id_campo == item.id_campo,
            ValorCampoPersonalizado.id_entidad == id_entidad
        )).first()
        
        if existing:
            existing.valor = item.valor
            existing.fecha_actualizacion = datetime.utcnow()
            session.add(existing)
        else:
            new_val = ValorCampoPersonalizado(
                id_campo=item.id_campo,
                id_entidad=id_entidad,
                valor=item.valor,
                fecha_actualizacion=datetime.utcnow()
            )
            session.add(new_val)
    
    session.commit()
    return {"status": "success", "count": len(data.values)}
