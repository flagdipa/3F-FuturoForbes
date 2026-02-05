from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class PluginBase(BaseModel):
    nombre_tecnico: str
    nombre_display: str
    descripcion: Optional[str] = None
    version: str = "1.0.0"
    autor: str = "3F Core"

class PluginCreate(PluginBase):
    pass

class PluginUpdate(BaseModel):
    nombre_display: Optional[str] = None
    descripcion: Optional[str] = None
    version: Optional[str] = None
    activo: Optional[bool] = None
    configuracion: Optional[Dict[str, Any]] = None
    hooks_suscritos: Optional[str] = None

class PluginRead(PluginBase):
    id_plugin: int
    instalado: bool
    activo: bool
    configuracion: Dict[str, Any]
    hooks_suscritos: str
    creado_el: datetime
    actualizado_el: datetime

    class Config:
        from_attributes = True
