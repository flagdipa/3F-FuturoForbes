"""
API Router for System Configurations
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from ...core.database import get_session
from ...models.models_config import Configuracion
from .schemas import ConfigResponse, ConfigUpdate, ConfigBase

router = APIRouter(prefix="/settings", tags=["Configuration"])

@router.get("/", response_model=List[ConfigResponse])
def list_settings(session: Session = Depends(get_session)):
    """List all system settings"""
    return session.exec(select(Configuracion)).all()

@router.get("/{clave}", response_model=ConfigResponse)
def get_setting(clave: str, session: Session = Depends(get_session)):
    """Get a specific setting by key"""
    setting = session.get(Configuracion, clave)
    if not setting:
        raise HTTPException(status_code=404, detail=f"Configuración '{clave}' no encontrada")
    return setting

@router.put("/{clave}", response_model=ConfigResponse)
def update_setting(
    clave: str, 
    data: ConfigUpdate, 
    session: Session = Depends(get_session)
):
    """Update an existing setting value"""
    setting = session.get(Configuracion, clave)
    if not setting:
        # Check if we should allow creating on the fly via PUT (Upsert)
        setting = Configuracion(clave=clave, **data.dict())
    else:
        setting.valor = data.valor
        if data.descripcion is not None:
            setting.descripcion = data.descripcion
    
    setting.fecha_actualizacion = datetime.utcnow()
    session.add(setting)
    session.commit()
    session.refresh(setting)
    return setting

@router.post("/", response_model=ConfigResponse, status_code=status.HTTP_201_CREATED)
def create_setting(data: ConfigBase, session: Session = Depends(get_session)):
    """Add a new system setting"""
    existing = session.get(Configuracion, data.clave)
    if existing:
        raise HTTPException(status_code=400, detail=f"La configuración '{data.clave}' ya existe")
        
    setting = Configuracion(**data.dict())
    setting.fecha_actualizacion = datetime.utcnow()
    session.add(setting)
    session.commit()
    session.refresh(setting)
    return setting

@router.delete("/{clave}", status_code=status.HTTP_204_NO_CONTENT)
def delete_setting(clave: str, session: Session = Depends(get_session)):
    """Remove a system setting"""
    setting = session.get(Configuracion, clave)
    if not setting:
        raise HTTPException(status_code=404, detail=f"Configuración '{clave}' no encontrada")
        
    session.delete(setting)
    session.commit()
    return None
