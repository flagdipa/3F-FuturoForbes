from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import ConfigDict

class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"
    
    id_log: Optional[int] = Field(default=None, primary_key=True)
    fecha: datetime = Field(default_factory=datetime.utcnow, index=True)
    id_usuario: int = Field(index=True)
    accion: str = Field(index=True) # CREATE, UPDATE, DELETE, LOGIN, EXPORT, etc.
    entidad: str = Field(index=True) # Transaccion, Cuenta, Activo, etc.
    id_entidad: Optional[int] = None
    detalles: str = Field(default="{}") # JSON string with changes or extra info
    ip_address: Optional[str] = None
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
