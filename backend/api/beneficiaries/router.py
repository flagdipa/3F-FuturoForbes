from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select, func
from ...core.database import get_session
from ...models.models import Beneficiario, Usuario, LibroTransacciones
from .schemas import BeneficiarioCrear, BeneficiarioLectura, BeneficiarioUpdate
from ..base_crud import BaseCRUDService
from ..schemas.common import PaginatedResponse, PaginationMetadata
from ..auth.deps import get_current_user
from typing import List

router = APIRouter(prefix="/beneficiarios", tags=["Beneficiarios"])

# Initialize generic service
beneficiary_service = BaseCRUDService[Beneficiario, BeneficiarioCrear, BeneficiarioUpdate](Beneficiario)

@router.get("/", response_model=PaginatedResponse[BeneficiarioLectura])
def listar_beneficiarios(
    offset: int = 0,
    limit: int = 500, # Increased default limit for managers
    session: Session = Depends(get_session)
):
    """List all beneficiaries with usage count"""
    # Build subquery for usage counts
    sub_count = (
        select(
            LibroTransacciones.id_beneficiario,
            func.count(LibroTransacciones.id_transaccion).label("cnt")
        )
        .group_by(LibroTransacciones.id_beneficiario)
        .subquery()
    )

    # Main query joining with beneficiary
    query = (
        select(Beneficiario, func.coalesce(sub_count.c.cnt, 0))
        .outerjoin(sub_count, Beneficiario.id_beneficiario == sub_count.c.id_beneficiario)
        .order_by(Beneficiario.nombre_beneficiario)
    )

    total = session.exec(select(func.count()).select_from(Beneficiario)).one()
    results = session.exec(query.offset(offset).limit(limit)).all()
    
    data = []
    for benef, count in results:
        # We manually map the count to the schema
        item = BeneficiarioLectura.from_orm(benef)
        item.transacciones_count = count
        data.append(item)

    return PaginatedResponse(
        data=data,
        pagination=PaginationMetadata(
            total=total,
            offset=offset,
            limit=limit,
            has_more=(offset + limit) < total
        )
    )

@router.post("/", response_model=BeneficiarioLectura)
def crear_beneficiario(
    beneficiario_in: BeneficiarioCrear, 
    request: Request,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Create a new beneficiary with audit"""
    return beneficiary_service.create(
        session, 
        beneficiario_in,
        user_id=current_user.id_usuario,
        ip_address=request.client.host
    )

@router.get("/{beneficiario_id}", response_model=BeneficiarioLectura)
def obtener_beneficiario(beneficiario_id: int, session: Session = Depends(get_session)):
    """Get a beneficiary by ID"""
    benef = beneficiary_service.get(session, beneficiario_id)
    if not benef:
        raise HTTPException(status_code=404, detail="Beneficiario no encontrado")
    return benef

@router.put("/{beneficiario_id}", response_model=BeneficiarioLectura)
def actualizar_beneficiario(
    beneficiario_id: int,
    beneficiario_in: BeneficiarioUpdate,
    request: Request,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Update a beneficiary with audit"""
    db_obj = beneficiary_service.get(session, beneficiario_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Beneficiario no encontrado")
    
    return beneficiary_service.update(
        session,
        db_obj=db_obj,
        obj_in=beneficiario_in,
        user_id=current_user.id_usuario,
        ip_address=request.client.host
    )

@router.delete("/{beneficiario_id}")
def eliminar_beneficiario(
    beneficiario_id: int, 
    request: Request,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Delete a beneficiary with audit"""
    success = beneficiary_service.delete(
        session, 
        beneficiario_id,
        user_id=current_user.id_usuario,
        ip_address=request.client.host
    )
    if not success:
        raise HTTPException(status_code=404, detail="Beneficiario no encontrado")
    return {"message": "Beneficiario eliminado correctamente"}
