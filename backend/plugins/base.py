"""
Base Plugin - Clase base para todos los plugins de 3F
Implementación Pura estilo PrestaShop
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import logging

class BasePlugin(ABC):
    """
    Clase base abstracta que todos los plugins de 3F deben heredar.
    Proporciona la estructura mínima requerida para instalación, activación
    y gestión de hooks del ciclo de vida.
    """
    
    name: str = ""
    version: str = "1.0.0"
    author: str = ""
    description: str = ""
    hooks: List[str] = []
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"plugin.{self.name or self.__class__.__name__}")
        
    @abstractmethod
    def install(self) -> bool:
        """Crear tablas, configs por defecto, registrar estados iniciales"""
        return True

    @abstractmethod
    def uninstall(self) -> bool:
        """Eliminar tablas, datos y configuraciones huérfanas"""
        return True

    def activate(self) -> bool:
        """Llamado cuando el plugin se enciende"""
        return True

    def deactivate(self) -> bool:
        """Llamado cuando el plugin se apaga temporalmente"""
        return True

    def get_config_schema(self) -> dict:
        """Retorna un JSON Schema estándar form para auto-generar la UI de admin si no hay una custom"""
        return {}

    def get_config(self, key: str = None, default: Any = None) -> Any:
        """Retorna la configuración actual (o una key específica)"""
        if key:
            return self.config.get(key, default)
        return self.config

    def set_config(self, data: dict) -> bool:
        """Guarda parcial o totalmente nueva config"""
        self.config.update(data)
        return True

    def render_config_page(self) -> str:
        """HTML opcional puro que reemplaza el auto-generado de 'get_config_schema'"""
        return ""
