from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, JSON, Column

class Plugin(SQLModel, table=True):
    """
    Representa un módulo o plugin del sistema.
    Inspirado en la arquitectura modular de PrestaShop.
    """
    __tablename__ = "plugins"
    
    id_plugin: Optional[int] = Field(default=None, primary_key=True)
    nombre_tecnico: str = Field(unique=True, index=True) # ej: "ia_ocr", "gmail_connector"
    nombre_display: str
    descripcion: Optional[str] = None
    version: str = "1.0.0"
    autor: str = "3F Core"
    
    # Estados del ciclo de vida
    instalado: bool = Field(default=False)
    activo: bool = Field(default=False)
    
    # Metadatos flexibles
    configuracion: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    hooks_suscritos: str = Field(default="") # Lista separada por comas de hooks
    
    creado_el: datetime = Field(default_factory=datetime.utcnow)
    actualizado_el: datetime = Field(default_factory=datetime.utcnow)
