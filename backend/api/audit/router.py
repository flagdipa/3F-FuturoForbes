from fastapi import APIRouter, Depends, Query, Request
from sqlmodel import Session
from ...core.database import get_session
from ..auth.deps import get_current_user
from ...models.models import Usuario
from ...models.models_audit import AuditLog
from ..base_crud import BaseCRUDService
from ..schemas.common import PaginatedResponse
from typing import List, Optional

router = APIRouter(prefix="/audit", tags=["Security Audit"])
audit_crud = BaseCRUDService(AuditLog)

@router.get("/logs", response_model=PaginatedResponse[AuditLog])
def get_audit_logs(
    offset: int = 0,
    limit: int = 50,
    accion: Optional[str] = None,
    entidad: Optional[str] = None,
    id_usuario: Optional[int] = None,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Retrieves audit logs. 
    In the future, this will be filtered by admin role.
    For now, users see all logs (beta simplicity).
    """
    filters = {}
    if accion: filters["accion"] = accion
    if entidad: filters["entidad"] = entidad
    if id_usuario: filters["id_usuario"] = id_usuario
    
    return audit_crud.list(session, offset=offset, limit=limit, filters=filters)
