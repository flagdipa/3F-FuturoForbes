from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from ...core.database import get_session
from ...models.models import Divisa
from .schemas_divisa import DivisaCrear, DivisaLectura
from typing import List

router = APIRouter(prefix="/divisas", tags=["Divisas"]) # Renombrado

@router.get("/", response_model=List[DivisaLectura])
def listar_divisas(session: Session = Depends(get_session)):
    return session.exec(select(Divisa)).all()

@router.post("/", response_model=DivisaLectura)
def crear_divisa(divisa_in: DivisaCrear, session: Session = Depends(get_session)):
    nueva_divisa = Divisa.from_orm(divisa_in)
    session.add(nueva_divisa)
    session.commit()
    session.refresh(nueva_divisa)
    return nueva_divisa
