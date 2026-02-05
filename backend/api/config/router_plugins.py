from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from datetime import datetime
from ...core.database import get_session
from ...models.models_plugins import Plugin
from .schemas_plugins import PluginRead, PluginCreate, PluginUpdate
from ..auth.deps import get_current_user

router = APIRouter(prefix="/plugins", tags=["Plugins"], dependencies=[Depends(get_current_user)])

@router.get("/", response_model=List[PluginRead])
def listar_plugins(session: Session = Depends(get_session)):
    """Listar todos los módulos instalados en el sistema"""
    return session.exec(select(Plugin)).all()

@router.post("/", response_model=PluginRead, status_code=status.HTTP_201_CREATED)
def registrar_plugin(plugin_in: PluginCreate, session: Session = Depends(get_session)):
    """Registrar un nuevo módulo en la base de datos"""
    # Verificar si ya existe
    db_plugin = session.exec(select(Plugin).where(Plugin.nombre_tecnico == plugin_in.nombre_tecnico)).first()
    if db_plugin:
        raise HTTPException(status_code=400, detail="El plugin ya está registrado")
    
    new_plugin = Plugin(**plugin_in.dict(), instalado=True, activo=True)
    session.add(new_plugin)
    session.commit()
    session.refresh(new_plugin)
    return new_plugin

@router.patch("/{plugin_id}", response_model=PluginRead)
def actualizar_estado_plugin(
    plugin_id: int, 
    plugin_in: PluginUpdate, 
    session: Session = Depends(get_session)
):
    """Activar/Desactivar o configurar un módulo"""
    db_plugin = session.get(Plugin, plugin_id)
    if not db_plugin:
        raise HTTPException(status_code=404, detail="Plugin no encontrado")
    
    plugin_data = plugin_in.dict(exclude_unset=True)
    for key, value in plugin_data.items():
        setattr(db_plugin, key, value)
    
    db_plugin.actualizado_el = datetime.utcnow()
    session.add(db_plugin)
    session.commit()
    session.refresh(db_plugin)
    return db_plugin

@router.delete("/{plugin_id}", status_code=status.HTTP_204_NO_CONTENT)
def desinstalar_plugin(plugin_id: int, session: Session = Depends(get_session)):
    """Remover un módulo del sistema"""
    db_plugin = session.get(Plugin, plugin_id)
    if not db_plugin:
        raise HTTPException(status_code=404, detail="Plugin no encontrado")
    
    session.delete(db_plugin)
    session.commit()
    return None
