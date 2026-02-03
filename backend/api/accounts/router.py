from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from ...core.database import get_session
from ...models.models import ListaCuentas
from .schemas import CuentaCrear, CuentaLectura
from typing import List

router = APIRouter(prefix="/cuentas", tags=["Cuentas"]) # Renombrado

@router.get("/", response_model=List[CuentaLectura])
def listar_cuentas(session: Session = Depends(get_session)):
    return session.exec(select(ListaCuentas)).all()

@router.post("/", response_model=CuentaLectura)
def crear_cuenta(cuenta_in: CuentaCrear, session: Session = Depends(get_session)):
    # Verificar si el nombre ya existe
    existing = session.exec(select(ListaCuentas).where(ListaCuentas.nombre_cuenta == cuenta_in.nombre_cuenta)).first()
    if existing:
        raise HTTPException(status_code=400, detail="El nombre de cuenta ya existe")
    
    nueva_cuenta = ListaCuentas.from_orm(cuenta_in)
    session.add(nueva_cuenta)
    session.commit()
    session.refresh(nueva_cuenta)
    return nueva_cuenta

@router.get("/{cuenta_id}", response_model=CuentaLectura)
def obtener_cuenta(cuenta_id: int, session: Session = Depends(get_session)):
    cuenta = session.get(ListaCuentas, cuenta_id)
    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    return cuenta
