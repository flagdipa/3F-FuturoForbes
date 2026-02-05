from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ...core.database import get_session
from ...models.models import Beneficiario
from .schemas import BeneficiarioCrear, BeneficiarioLectura
from ..base_crud import BaseCRUDService
from ..schemas.common import PaginatedResponse
from typing import List

router = APIRouter(prefix="/beneficiarios", tags=["Beneficiarios"])

# Initialize generic service
beneficiary_service = BaseCRUDService[Beneficiario, BeneficiarioCrear, BeneficiarioCrear](Beneficiario)

@router.get("/", response_model=PaginatedResponse[BeneficiarioLectura])
def listar_beneficiarios(
    offset: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """List all beneficiaries with pagination"""
    return beneficiary_service.list(session, offset, limit)

@router.post("/", response_model=BeneficiarioLectura)
def crear_beneficiario(beneficiario_in: BeneficiarioCrear, session: Session = Depends(get_session)):
    """Create a new beneficiary"""
    return beneficiary_service.create(session, beneficiario_in)

@router.get("/{beneficiario_id}", response_model=BeneficiarioLectura)
def obtener_beneficiario(beneficiario_id: int, session: Session = Depends(get_session)):
    """Get a beneficiary by ID"""
    benef = beneficiary_service.get(session, beneficiario_id)
    if not benef:
        raise HTTPException(status_code=404, detail="Beneficiario no encontrado")
    return benef

@router.delete("/{beneficiario_id}")
def eliminar_beneficiario(beneficiario_id: int, session: Session = Depends(get_session)):
    """Delete a beneficiary"""
    success = beneficiary_service.delete(session, beneficiario_id)
    if not success:
        raise HTTPException(status_code=404, detail="Beneficiario no encontrado")
    return {"message": "Beneficiario eliminado correctamente"}
