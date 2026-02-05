from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session, select
from ...core.database import get_session
from ...models.models import ListaCuentas, Usuario
from .schemas import CuentaCrear, CuentaLectura
from ..base_crud import BaseCRUDService
from ..schemas.common import PaginatedResponse
from ..auth.deps import get_current_user
from typing import List

router = APIRouter(prefix="/cuentas", tags=["Cuentas"])

# Initialize generic service
account_service = BaseCRUDService[ListaCuentas, CuentaCrear, CuentaCrear](ListaCuentas)

@router.get("/", response_model=PaginatedResponse[CuentaLectura])
def listar_cuentas(
    offset: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """List all accounts with pagination"""
    return account_service.list(session, offset, limit)

@router.post("/", response_model=CuentaLectura)
def crear_cuenta(
    cuenta_in: CuentaCrear, 
    request: Request,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Create a new account with uniqueness check and audit"""
    existing = session.exec(select(ListaCuentas).where(ListaCuentas.nombre_cuenta == cuenta_in.nombre_cuenta)).first()
    if existing:
        raise HTTPException(status_code=400, detail="El nombre de cuenta ya existe")
    
    return account_service.create(
        session, 
        cuenta_in, 
        user_id=current_user.id_usuario, 
        ip_address=request.client.host
    )

@router.get("/{cuenta_id}", response_model=CuentaLectura)
def obtener_cuenta(cuenta_id: int, session: Session = Depends(get_session)):
    """Get an account by ID"""
    cuenta = account_service.get(session, cuenta_id)
    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    return cuenta

@router.delete("/{cuenta_id}")
def eliminar_cuenta(
    cuenta_id: int, 
    request: Request,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Delete an account with audit"""
    success = account_service.delete(
        session, 
        cuenta_id, 
        user_id=current_user.id_usuario, 
        ip_address=request.client.host
    )
    if not success:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    return {"message": "Cuenta eliminada correctamente"}
