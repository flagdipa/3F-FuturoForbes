from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ...core.database import get_session
from ...models.models import Beneficiario
from .schemas import BeneficiarioCrear, BeneficiarioLectura
from typing import List

router = APIRouter(prefix="/beneficiarios", tags=["Beneficiarios"]) # Renombrado

@router.get("/", response_model=List[BeneficiarioLectura])
def listar_beneficiarios(session: Session = Depends(get_session)):
    return session.exec(select(Beneficiario)).all()

@router.post("/", response_model=BeneficiarioLectura)
def crear_beneficiario(beneficiario_in: BeneficiarioCrear, session: Session = Depends(get_session)):
    nuevo_beneficiario = Beneficiario.from_orm(beneficiario_in)
    session.add(nuevo_beneficiario)
    session.commit()
    session.refresh(nuevo_beneficiario)
    return nuevo_beneficiario
