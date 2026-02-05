import json
import logging
from datetime import datetime
from typing import Optional, Any, Dict
from sqlmodel import Session
from ..models.models_audit import AuditLog

logger = logging.getLogger(__name__)

class AuditService:
    @staticmethod
    def log(
        session: Session,
        user_id: int,
        accion: str,
        entidad: str,
        id_entidad: Optional[int] = None,
        detalles: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ):
        """
        Records an event in the audit trail.
        """
        try:
            log_entry = AuditLog(
                fecha=datetime.utcnow(),
                id_usuario=user_id,
                accion=accion,
                entidad=entidad,
                id_entidad=id_entidad,
                detalles=json.dumps(detalles) if detalles else "{}",
                ip_address=ip_address
            )
            session.add(log_entry)
            session.commit()
            logger.info(f"Audit: User {user_id} performed {accion} on {entidad} ({id_entidad})")
        except Exception as e:
            logger.error(f"Failed to record audit log: {e}")
            # We don't want to crash the main request if auditing fails, 
            # but we should log it.

audit_service = AuditService()
