from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlmodel import Session, select, func
from typing import List, Optional
from backend.core.database import get_session
from backend.models.models_extended import Etiqueta, TransaccionEtiqueta
from backend.models.models import Usuario
from .schemas import (
    EtiquetaCreate, EtiquetaUpdate, EtiquetaResponse, EtiquetaConConteo,
    TransaccionEtiquetaCreate, TransaccionEtiquetaResponse
)
from ..base_crud import BaseCRUDService
from ..schemas.common import PaginatedResponse
from ..auth.deps import get_current_user

router = APIRouter(prefix="/tags", tags=["Tags"])

# Initialize generic service
tag_service = BaseCRUDService[Etiqueta, EtiquetaCreate, EtiquetaUpdate](Etiqueta)

# ==================== ETIQUETAS CRUD ====================

@router.get("/", response_model=PaginatedResponse[EtiquetaResponse])
def list_tags(
    offset: int = 0,
    limit: int = 100,
    activo: Optional[int] = None,
    session: Session = Depends(get_session)
):
    """List all tags with pagination and optional active filter"""
    filters = {}
    if activo is not None:
        filters["activo"] = activo
    
    return tag_service.list(session, offset, limit, filters=filters)

@router.get("/with-counts", response_model=List[EtiquetaConConteo])
def list_tags_with_counts(session: Session = Depends(get_session)):
    """List all tags with usage counts (special non-paginated view)"""
    query = (
        select(Etiqueta, func.count(TransaccionEtiqueta.id_transaccion).label("conteo_uso"))
        .outerjoin(TransaccionEtiqueta, Etiqueta.id_etiqueta == TransaccionEtiqueta.id_etiqueta)
        .group_by(Etiqueta.id_etiqueta)
        .order_by(Etiqueta.nombre_etiqueta)
    )
    
    results = session.exec(query).all()
    return [
        EtiquetaConConteo(**tag.dict(), conteo_uso=count)
        for tag, count in results
    ]

@router.get("/{id_etiqueta}", response_model=EtiquetaResponse)
def get_tag(id_etiqueta: int, session: Session = Depends(get_session)):
    """Get a specific tag by ID"""
    tag = tag_service.get(session, id_etiqueta)
    if not tag:
        raise HTTPException(status_code=404, detail="Etiqueta no encontrada")
    return tag

@router.post("/", response_model=EtiquetaResponse, status_code=status.HTTP_201_CREATED)
def create_tag(
    tag_data: EtiquetaCreate, 
    request: Request,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Create a new tag with duplicate check and audit"""
    existing = session.exec(
        select(Etiqueta).where(Etiqueta.nombre_etiqueta == tag_data.nombre_etiqueta)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe una etiqueta con el nombre '{tag_data.nombre_etiqueta}'"
        )
    
    return tag_service.create(
        session, tag_data, 
        user_id=current_user.id_usuario, 
        ip_address=request.client.host
    )

@router.put("/{id_etiqueta}", response_model=EtiquetaResponse)
def update_tag(
    id_etiqueta: int,
    tag_data: EtiquetaUpdate,
    request: Request,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Update an existing tag with audit"""
    tag = tag_service.get(session, id_etiqueta)
    if not tag:
        raise HTTPException(status_code=404, detail="Etiqueta no encontrada")
    
    # Check for duplicate name if changing name
    if tag_data.nombre_etiqueta and tag_data.nombre_etiqueta != tag.nombre_etiqueta:
        existing = session.exec(
            select(Etiqueta).where(Etiqueta.nombre_etiqueta == tag_data.nombre_etiqueta)
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe una etiqueta con el nombre '{tag_data.nombre_etiqueta}'"
            )
    
    return tag_service.update(
        session, tag, tag_data,
        user_id=current_user.id_usuario,
        ip_address=request.client.host
    )

@router.delete("/{id_etiqueta}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    id_etiqueta: int, 
    request: Request,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Delete a tag with audit"""
    success = tag_service.delete(
        session, id_etiqueta,
        user_id=current_user.id_usuario,
        ip_address=request.client.host
    )
    if not success:
        raise HTTPException(status_code=404, detail="Etiqueta no encontrada")
    return None


# ==================== TRANSACTION TAGGING ====================

@router.get("/transaction/{id_transaccion}", response_model=List[EtiquetaResponse])
def get_transaction_tags(id_transaccion: int, session: Session = Depends(get_session)):
    """Get all tags for a specific transaction"""
    query = (
        select(Etiqueta)
        .join(TransaccionEtiqueta)
        .where(TransaccionEtiqueta.id_transaccion == id_transaccion)
        .order_by(Etiqueta.nombre_etiqueta)
    )
    
    tags = session.exec(query).all()
    return tags


@router.post("/transaction/{id_transaccion}", status_code=status.HTTP_201_CREATED)
def add_tag_to_transaction(
    id_transaccion: int,
    tag_data: TransaccionEtiquetaCreate,
    session: Session = Depends(get_session)
):
    """Add a tag to a transaction"""
    # Check if already tagged
    existing = session.exec(
        select(TransaccionEtiqueta).where(
            TransaccionEtiqueta.id_transaccion == id_transaccion,
            TransaccionEtiqueta.id_etiqueta == tag_data.id_etiqueta
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="La transacción ya tiene esta etiqueta"
        )
    
    # Verify tag exists
    tag = session.get(Etiqueta, tag_data.id_etiqueta)
    if not tag:
        raise HTTPException(status_code=404, detail="Etiqueta no encontrada")
    
    trans_tag = TransaccionEtiqueta(
        id_transaccion=id_transaccion,
        id_etiqueta=tag_data.id_etiqueta
    )
    session.add(trans_tag)
    session.commit()
    
    return {"message": "Etiqueta agregada exitosamente"}


@router.delete("/transaction/{id_transaccion}/{id_etiqueta}", status_code=status.HTTP_204_NO_CONTENT)
def remove_tag_from_transaction(
    id_transaccion: int,
    id_etiqueta: int,
    session: Session = Depends(get_session)
):
    """Remove a tag from a transaction"""
    trans_tag = session.exec(
        select(TransaccionEtiqueta).where(
            TransaccionEtiqueta.id_transaccion == id_transaccion,
            TransaccionEtiqueta.id_etiqueta == id_etiqueta
        )
    ).first()
    
    if not trans_tag:
        raise HTTPException(status_code=404, detail="Relación no encontrada")
    
    session.delete(trans_tag)
    session.commit()
    return None
