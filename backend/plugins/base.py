"""
Base Plugin - Clase base para todos los plugins de 3F
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import logging


class BasePlugin(ABC):
    """
    Clase base abstracta que todos los plugins deben heredar.
    Proporciona la estructura mínima necesaria para integrarse con el sistema.
    """
    
    # Atributos que deben ser definidos por cada plugin
    nombre_tecnico: str = ""
    nombre_display: str = ""
    version: str = "1.0.0"
    autor: str = ""
    descripcion: str = ""
    hooks: List[str] = []
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Inicializar el plugin.
        
        Args:
            config: Diccionario de configuración del plugin
        """
        self.config = config or {}
        self.logger = logging.getLogger(self.nombre_tecnico or __name__)
        
        # Validar que el plugin defina los atributos necesarios
        if not self.nombre_tecnico:
            raise ValueError(f"Plugin {self.__class__.__name__} debe definir 'nombre_tecnico'")
        
        if not self.nombre_display:
            self.nombre_display = self.nombre_tecnico
    
    @abstractmethod
    async def initialize(self):
        """
        Inicializar el plugin.
        Este método se llama cuando el plugin se carga en memoria.
        Aquí se deben realizar todas las configuraciones iniciales.
        """
        pass
    
    @abstractmethod
    async def shutdown(self):
        """
        Cerrar el plugin de forma segura.
        Este método se llama cuando el plugin se desactiva.
        Aquí se deben liberar recursos y cerrar conexiones.
        """
        pass
    
    async def on_hook(self, hook_name: str, **kwargs):
        """
        Manejar un hook específico.
        Este método busca un handler específico para el hook y lo ejecuta.
        
        Args:
            hook_name: Nombre del hook disparado
            **kwargs: Parámetros del hook
        """
        # Buscar método handler específico (on_<hook_name>)
        handler_name = f"on_{hook_name}"
        handler = getattr(self, handler_name, None)
        
        if handler and callable(handler):
            try:
                await handler(**kwargs)
            except Exception as e:
                self.logger.error(f"Error en handler '{handler_name}': {e}")
                raise
        else:
            self.logger.warning(f"No se encontró handler para hook '{hook_name}'")
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Obtener un valor de configuración.
        
        Args:
            key: Clave de configuración
            default: Valor por defecto si no existe
            
        Returns:
            Valor de configuración o default
        """
        return self.config.get(key, default)
    
    def validate_config(self, required_keys: List[str]):
        """
        Validar que la configuración tenga las claves requeridas.
        
        Args:
            required_keys: Lista de claves requeridas
            
        Raises:
            ValueError: Si falta alguna clave requerida
        """
        missing = [key for key in required_keys if key not in self.config]
        if missing:
            raise ValueError(f"Configuración incompleta. Faltan claves: {', '.join(missing)}")
    
    def get_info(self) -> Dict[str, Any]:
        """
        Obtener información del plugin.
        
        Returns:
            Diccionario con información del plugin
        """
        return {
            "nombre_tecnico": self.nombre_tecnico,
            "nombre_display": self.nombre_display,
            "version": self.version,
            "autor": self.autor,
            "descripcion": self.descripcion,
            "hooks": self.hooks,
            "config": self.config
        }
