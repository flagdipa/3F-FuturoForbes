"""
Base Plugin - Clase base para todos los plugins de 3F
Implementación Pura estilo PrestaShop
"""
from typing import Dict, Any, List
import logging

class BasePlugin:
    """
    Clase base que todos los plugins de 3F deben heredar.
    Proporciona la estructura mínima requerida para instalación, activación
    y gestión de hooks del ciclo de vida.

    Convención de hooks:
    - Métodos con prefijo 'hook_' → registran en el PluginManager (estilo antiguo)
    - Métodos con prefijo 'on_'   → igual, registran en el PluginManager (estilo nuevo)
    Ambos prefijos son reconocidos por el motor de hooks.
    """

    # Atributos que los plugins deben definir en su clase
    technical_name: str = ""
    display_name: str = ""
    name: str = ""           # alias inglés (retrocompatibilidad)
    version: str = "1.0.0"
    autor: str = ""
    author: str = ""         # alias inglés (retrocompatibilidad)
    descripcion: str = ""
    description: str = ""    # alias inglés (retrocompatibilidad)
    hooks: List[str] = []

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        plugin_name = (
            self.technical_name
            or self.name
            or self.__class__.__name__
        )
        self.logger = logging.getLogger(f"plugin.{plugin_name}")

    def install(self) -> bool:
        """Crear tablas, configs por defecto, registrar estados iniciales.
        Sobreescribir en el plugin si se necesita lógica especial."""
        return True

    def uninstall(self) -> bool:
        """Eliminar tablas, datos y configuraciones huérfanas.
        Sobreescribir en el plugin si se necesita lógica especial."""
        return True

    def activate(self) -> bool:
        """Llamado cuando el plugin se enciende."""
        return True

    def deactivate(self) -> bool:
        """Llamado cuando el plugin se apaga temporalmente."""
        return True

    def get_config_schema(self) -> dict:
        """Retorna un JSON Schema estándar para auto-generar la UI de admin."""
        return {}

    def get_config(self, key: str = None, default: Any = None) -> Any:
        """Retorna la configuración actual (o una key específica)."""
        if key:
            return self.config.get(key, default)
        return self.config

    def set_config(self, data: dict) -> bool:
        """Guarda parcial o totalmente nueva config."""
        self.config.update(data)
        return True

    def render_config_page(self) -> str:
        """HTML opcional que reemplaza el auto-generado de 'get_config_schema'."""
        return ""
