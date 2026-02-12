"""
Financial Entities API Router
CRUD for entity types (Banco, Broker, Fintech) and specific institutions (Santander, Balanz)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from backend.core.database import get_session
from backend.models.models import TipoEntidadFinanciera, IdentidadFinanciera
from .schemas import (
    TipoEntidadCreate, TipoEntidadUpdate, TipoEntidadResponse,
    IdentidadFinancieraCreate, IdentidadFinancieraUpdate, IdentidadFinancieraResponse,
    TipoEntidadConEntidades
)

router = APIRouter(prefix="/financial-entities", tags=["Financial Entities"])


# ==================== TIPOS DE ENTIDAD ====================

@router.get("/types", response_model=List[TipoEntidadResponse])
def list_entity_types(
    include_inactive: bool = False,
    session: Session = Depends(get_session)
):
    """List all entity types (Banco, Broker, Fintech, etc.)"""
    query = select(TipoEntidadFinanciera)
    if not include_inactive:
        query = query.where(TipoEntidadFinanciera.activo == True)
    return session.exec(query.order_by(TipoEntidadFinanciera.nombre_tipo)).all()


@router.get("/types/{id_tipo}", response_model=TipoEntidadConEntidades)
def get_entity_type(id_tipo: int, session: Session = Depends(get_session)):
    """Get entity type with its institutions"""
    tipo = session.get(TipoEntidadFinanciera, id_tipo)
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de entidad no encontrado")
    
    # Get entities of this type
    entities = session.exec(
        select(IdentidadFinanciera)
        .where(IdentidadFinanciera.id_tipo == id_tipo)
        .where(IdentidadFinanciera.activo == True)
    ).all()
    
    return TipoEntidadConEntidades(
        **tipo.model_dump(),
        entidades=[IdentidadFinancieraResponse(**e.model_dump()) for e in entities]
    )


@router.post("/types", response_model=TipoEntidadResponse, status_code=status.HTTP_201_CREATED)
def create_entity_type(data: TipoEntidadCreate, session: Session = Depends(get_session)):
    """Create a new entity type"""
    # Check uniqueness
    existing = session.exec(
        select(TipoEntidadFinanciera).where(TipoEntidadFinanciera.nombre_tipo == data.nombre_tipo)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un tipo con ese nombre")
    
    tipo = TipoEntidadFinanciera(**data.model_dump())
    session.add(tipo)
    session.commit()
    session.refresh(tipo)
    return tipo


@router.put("/types/{id_tipo}", response_model=TipoEntidadResponse)
def update_entity_type(id_tipo: int, data: TipoEntidadUpdate, session: Session = Depends(get_session)):
    """Update an entity type"""
    tipo = session.get(TipoEntidadFinanciera, id_tipo)
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de entidad no encontrado")
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tipo, key, value)
    
    session.add(tipo)
    session.commit()
    session.refresh(tipo)
    return tipo


@router.delete("/types/{id_tipo}")
def delete_entity_type(id_tipo: int, session: Session = Depends(get_session)):
    """Soft delete entity type (sets activo=False)"""
    tipo = session.get(TipoEntidadFinanciera, id_tipo)
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de entidad no encontrado")
    
    tipo.activo = False
    session.add(tipo)
    session.commit()
    return {"message": "Tipo de entidad desactivado"}


# ==================== IDENTIDADES FINANCIERAS ====================

@router.get("/institutions", response_model=List[IdentidadFinancieraResponse])
def list_institutions(
    id_tipo: int = None,
    include_inactive: bool = False,
    session: Session = Depends(get_session)
):
    """List all financial institutions, optionally filtered by type"""
    query = select(IdentidadFinanciera, TipoEntidadFinanciera).outerjoin(
        TipoEntidadFinanciera,
        IdentidadFinanciera.id_tipo == TipoEntidadFinanciera.id_tipo
    )
    
    if not include_inactive:
        query = query.where(IdentidadFinanciera.activo == True)
    if id_tipo:
        query = query.where(IdentidadFinanciera.id_tipo == id_tipo)
    
    results = session.exec(query.order_by(IdentidadFinanciera.nombre)).all()
    
    response = []
    for entity, tipo in results:
        resp = IdentidadFinancieraResponse(
            **entity.model_dump(),
            tipo_nombre=tipo.nombre_tipo if tipo else None,
            tipo_icono=tipo.icono if tipo else None,
            tipo_color=tipo.color if tipo else None
        )
        response.append(resp)
    
    return response


@router.get("/institutions/{id_identidad}", response_model=IdentidadFinancieraResponse)
def get_institution(id_identidad: int, session: Session = Depends(get_session)):
    """Get a specific financial institution"""
    result = session.exec(
        select(IdentidadFinanciera, TipoEntidadFinanciera)
        .outerjoin(TipoEntidadFinanciera, IdentidadFinanciera.id_tipo == TipoEntidadFinanciera.id_tipo)
        .where(IdentidadFinanciera.id_identidad == id_identidad)
    ).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Entidad financiera no encontrada")
    
    entity, tipo = result
    return IdentidadFinancieraResponse(
        **entity.model_dump(),
        tipo_nombre=tipo.nombre_tipo if tipo else None,
        tipo_icono=tipo.icono if tipo else None,
        tipo_color=tipo.color if tipo else None
    )


@router.post("/institutions", response_model=IdentidadFinancieraResponse, status_code=status.HTTP_201_CREATED)
def create_institution(data: IdentidadFinancieraCreate, session: Session = Depends(get_session)):
    """Create a new financial institution"""
    # Check uniqueness
    existing = session.exec(
        select(IdentidadFinanciera).where(IdentidadFinanciera.nombre == data.nombre)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe una entidad con ese nombre")
    
    # Validate tipo exists if provided
    if data.id_tipo:
        tipo = session.get(TipoEntidadFinanciera, data.id_tipo)
        if not tipo:
            raise HTTPException(status_code=400, detail="Tipo de entidad no encontrado")
    
    entity = IdentidadFinanciera(**data.model_dump())
    session.add(entity)
    session.commit()
    session.refresh(entity)
    
    # Get tipo info for response
    tipo = session.get(TipoEntidadFinanciera, entity.id_tipo) if entity.id_tipo else None
    
    return IdentidadFinancieraResponse(
        **entity.model_dump(),
        tipo_nombre=tipo.nombre_tipo if tipo else None,
        tipo_icono=tipo.icono if tipo else None,
        tipo_color=tipo.color if tipo else None
    )


@router.put("/institutions/{id_identidad}", response_model=IdentidadFinancieraResponse)
def update_institution(id_identidad: int, data: IdentidadFinancieraUpdate, session: Session = Depends(get_session)):
    """Update a financial institution"""
    entity = session.get(IdentidadFinanciera, id_identidad)
    if not entity:
        raise HTTPException(status_code=404, detail="Entidad financiera no encontrada")
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(entity, key, value)
    
    session.add(entity)
    session.commit()
    session.refresh(entity)
    
    tipo = session.get(TipoEntidadFinanciera, entity.id_tipo) if entity.id_tipo else None
    
    return IdentidadFinancieraResponse(
        **entity.model_dump(),
        tipo_nombre=tipo.nombre_tipo if tipo else None,
        tipo_icono=tipo.icono if tipo else None,
        tipo_color=tipo.color if tipo else None
    )


@router.delete("/institutions/{id_identidad}")
def delete_institution(id_identidad: int, session: Session = Depends(get_session)):
    """Soft delete institution (sets activo=False)"""
    entity = session.get(IdentidadFinanciera, id_identidad)
    if not entity:
        raise HTTPException(status_code=404, detail="Entidad financiera no encontrada")
    
    entity.activo = False
    session.add(entity)
    session.commit()
    return {"message": "Entidad financiera desactivada"}


# ==================== SEED DATA ====================

@router.post("/seed", status_code=status.HTTP_201_CREATED)
def seed_default_data(session: Session = Depends(get_session)):
    """Seed default entity types (run once for initial setup)"""
    
    default_types = [
        {"nombre_tipo": "Banco", "descripcion": "Entidad bancaria tradicional", "icono": "fa-university", "color": "#0d6efd"},
        {"nombre_tipo": "Broker", "descripcion": "Agente de bolsa / Sociedad de bolsa", "icono": "fa-chart-line", "color": "#198754"},
        {"nombre_tipo": "Fintech", "descripcion": "Empresa de tecnología financiera", "icono": "fa-mobile-alt", "color": "#6f42c1"},
        {"nombre_tipo": "Billetera Virtual", "descripcion": "Billetera digital / E-wallet", "icono": "fa-wallet", "color": "#fd7e14"},
        {"nombre_tipo": "Cooperativa", "descripcion": "Cooperativa de crédito", "icono": "fa-users", "color": "#20c997"},
        {"nombre_tipo": "Caja de Ahorro", "descripcion": "Caja de ahorro mutual", "icono": "fa-piggy-bank", "color": "#e83e8c"},
        {"nombre_tipo": "Exchange Crypto", "descripcion": "Exchange de criptomonedas", "icono": "fa-bitcoin", "color": "#f7931a"},
        {"nombre_tipo": "Otro", "descripcion": "Otro tipo de entidad financiera", "icono": "fa-building", "color": "#6c757d"},
    ]
    
    created = 0
    for tipo_data in default_types:
        existing = session.exec(
            select(TipoEntidadFinanciera).where(TipoEntidadFinanciera.nombre_tipo == tipo_data["nombre_tipo"])
        ).first()
        if not existing:
            session.add(TipoEntidadFinanciera(**tipo_data))
            created += 1
    
    session.commit()
    return {"message": f"Seed completado. {created} tipos creados."}
