from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from ...core.database import get_session, get_current_user
from ...models.models import Usuario
from ...models.models_audit import AuditLog
from typing import List, Optional

router = APIRouter(prefix="/audit", tags=["Security Audit"])

@router.get("/logs", response_model=List[AuditLog])
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
    query = select(AuditLog)
    
    if accion:
        query = query.where(AuditLog.accion == accion)
    if entidad:
        query = query.where(AuditLog.entidad == entidad)
    if id_usuario:
        query = query.where(AuditLog.id_usuario == id_usuario)
        
    query = query.order_by(AuditLog.fecha.desc()).offset(offset).limit(limit)
    return session.exec(query).all()
