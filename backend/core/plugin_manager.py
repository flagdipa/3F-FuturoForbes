"""
Plugin Manager - Sistema de gestión de plugins para 3F
"""
import logging
import importlib
import sys
from typing import Dict, List, Callable, Any, Optional
from pathlib import Path
from sqlmodel import Session, select
from datetime import datetime

from backend.core.database import engine
from backend.models.models_plugins import Plugin

logger = logging.getLogger(__name__)


class PluginManager:
    """
    Gestor central de plugins del sistema 3F.
    Maneja el registro de hooks, carga de plugins y su ejecución.
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern para asegurar una única instancia"""
        if cls._instance is None:
            cls._instance = super(PluginManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.hooks: Dict[str, List[Dict]] = {}
        self.loaded_plugins: Dict[str, Any] = {}
        self._initialized = True
        logger.info("PluginManager inicializado")
    
    async def load_plugins(self, session: Session = None):
        """
        Cargar todos los plugins activos desde la base de datos.
        
        Args:
            session: Sesión de base de datos (opcional, crea una nueva si no se proporciona)
        """
        close_session = False
        if session is None:
            session = Session(engine)
            close_session = True
        
        try:
            # Obtener plugins activos
            plugins = session.exec(
                select(Plugin).where(Plugin.activo == True, Plugin.instalado == True)
            ).all()
            
            logger.info(f"Cargando {len(plugins)} plugins activos...")
            
            for plugin_db in plugins:
                try:
                    await self._load_plugin_instance(plugin_db)
                except Exception as e:
                    logger.error(f"Error cargando plugin {plugin_db.nombre_tecnico}: {e}")
            
            logger.info(f"Plugins cargados: {list(self.loaded_plugins.keys())}")
            
        finally:
            if close_session:
                session.close()
    
    async def _load_plugin_instance(self, plugin_db: Plugin):
        """
        Cargar una instancia de plugin desde la base de datos.
        
        Args:
            plugin_db: Registro del plugin en la base de datos
        """
        nombre_tecnico = plugin_db.nombre_tecnico
        
        # Evitar cargar duplicados
        if nombre_tecnico in self.loaded_plugins:
            logger.warning(f"Plugin {nombre_tecnico} ya está cargado")
            return
        
        try:
            # Importar el módulo del plugin
            module_path = f"backend.plugins.{nombre_tecnico}.plugin"
            module = importlib.import_module(module_path)
            
            # Obtener la clase del plugin
            class_name = ''.join(word.capitalize() for word in nombre_tecnico.split('_')) + 'Plugin'
            plugin_class = getattr(module, class_name)
            
            # Crear instancia con configuración
            plugin_instance = plugin_class(config=plugin_db.configuracion)
            
            # Inicializar el plugin
            await plugin_instance.initialize()
            
            # Registrar hooks
            for hook_name in plugin_instance.hooks:
                self.register_hook(hook_name, plugin_db.id_plugin, plugin_instance)
            
            # Guardar referencia
            self.loaded_plugins[nombre_tecnico] = {
                "instance": plugin_instance,
                "db_id": plugin_db.id_plugin,
                "hooks": plugin_instance.hooks
            }
            
            logger.info(f"✅ Plugin {nombre_tecnico} v{plugin_instance.version} cargado")
            
        except ImportError as e:
            logger.error(f"❌ No se pudo importar plugin {nombre_tecnico}: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Error inicializando plugin {nombre_tecnico}: {e}")
            raise
    
    def register_hook(self, hook_name: str, plugin_id: int, plugin_instance: Any):
        """
        Registrar un callback para un hook específico.
        
        Args:
            hook_name: Nombre del hook
            plugin_id: ID del plugin en la base de datos
            plugin_instance: Instancia del plugin
        """
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        
        self.hooks[hook_name].append({
            "plugin_id": plugin_id,
            "instance": plugin_instance
        })
        
        logger.debug(f"Hook '{hook_name}' registrado para plugin ID {plugin_id}")
    
    async def call_hook(self, hook_name: str, **kwargs):
        """
        Ejecutar todos los callbacks registrados para un hook.
        Los errores en un plugin no afectan a los demás.
        
        Args:
            hook_name: Nombre del hook a disparar
            **kwargs: Parámetros para pasar a los callbacks
        """
        if hook_name not in self.hooks:
            return
        
        logger.debug(f"Disparando hook '{hook_name}' con {len(self.hooks[hook_name])} plugins")
        
        for hook_data in self.hooks[hook_name]:
            plugin_instance = hook_data["instance"]
            
            try:
                # Llamar al handler específico del hook
                await plugin_instance.on_hook(hook_name, **kwargs)
                
            except Exception as e:
                logger.error(f"❌ Error en plugin {plugin_instance.nombre_tecnico} para hook '{hook_name}': {e}")
                # Continuar con el siguiente plugin, no detener
                continue
    
    async def install_plugin(self, plugin_data: dict, session: Session) -> Plugin:
        """
        Instalar un nuevo plugin en el sistema.
        
        Args:
            plugin_data: Datos del plugin a instalar
            session: Sesión de base de datos
            
        Returns:
            El plugin creado en la base de datos
        """
        # Verificar si ya existe
        existing = session.exec(
            select(Plugin).where(Plugin.nombre_tecnico == plugin_data["nombre_tecnico"])
        ).first()
        
        if existing:
            raise ValueError(f"Plugin {plugin_data['nombre_tecnico']} ya existe")
        
        # Crear registro
        new_plugin = Plugin(
            nombre_tecnico=plugin_data["nombre_tecnico"],
            nombre_display=plugin_data.get("nombre_display", plugin_data["nombre_tecnico"]),
            descripcion=plugin_data.get("descripcion"),
            version=plugin_data.get("version", "1.0.0"),
            autor=plugin_data.get("autor", "3F User"),
            instalado=True,
            activo=False,  # Se activa manualmente después
            configuracion=plugin_data.get("configuracion", {}),
            hooks_suscritos=",".join(plugin_data.get("hooks", []))
        )
        
        session.add(new_plugin)
        session.commit()
        session.refresh(new_plugin)
        
        logger.info(f"📦 Plugin {new_plugin.nombre_tecnico} instalado (ID: {new_plugin.id_plugin})")
        return new_plugin
    
    async def activate_plugin(self, plugin_id: int, session: Session):
        """
        Activar un plugin y cargarlo en memoria.
        
        Args:
            plugin_id: ID del plugin a activar
            session: Sesión de base de datos
        """
        plugin_db = session.get(Plugin, plugin_id)
        if not plugin_db:
            raise ValueError(f"Plugin ID {plugin_id} no encontrado")
        
        if plugin_db.activo:
            logger.warning(f"Plugin {plugin_db.nombre_tecnico} ya está activo")
            return
        
        # Actualizar estado
        plugin_db.activo = True
        plugin_db.actualizado_el = datetime.utcnow()
        session.add(plugin_db)
        session.commit()
        
        # Cargar en memoria
        await self._load_plugin_instance(plugin_db)
        
        logger.info(f"▶️ Plugin {plugin_db.nombre_tecnico} activado")
    
    async def deactivate_plugin(self, plugin_id: int, session: Session):
        """
        Desactivar un plugin y descargarlo de memoria.
        
        Args:
            plugin_id: ID del plugin a desactivar
            session: Sesión de base de datos
        """
        plugin_db = session.get(Plugin, plugin_id)
        if not plugin_db:
            raise ValueError(f"Plugin ID {plugin_id} no encontrado")
        
        if not plugin_db.activo:
            logger.warning(f"Plugin {plugin_db.nombre_tecnico} ya está inactivo")
            return
        
        nombre_tecnico = plugin_db.nombre_tecnico
        
        # Remover de hooks
        if nombre_tecnico in self.loaded_plugins:
            plugin_data = self.loaded_plugins[nombre_tecnico]
            
            # Llamar shutdown
            try:
                await plugin_data["instance"].shutdown()
            except Exception as e:
                logger.error(f"Error en shutdown de {nombre_tecnico}: {e}")
            
            # Remover hooks
            for hook_name in plugin_data["hooks"]:
                if hook_name in self.hooks:
                    self.hooks[hook_name] = [
                        h for h in self.hooks[hook_name] 
                        if h["plugin_id"] != plugin_id
                    ]
            
            # Remover de loaded_plugins
            del self.loaded_plugins[nombre_tecnico]
        
        # Actualizar estado en BD
        plugin_db.activo = False
        plugin_db.actualizado_el = datetime.utcnow()
        session.add(plugin_db)
        session.commit()
        
        logger.info(f"⏸️ Plugin {nombre_tecnico} desactivado")
    
    def get_plugin_instance(self, nombre_tecnico: str) -> Optional[Any]:
        """
        Obtener la instancia de un plugin cargado.
        
        Args:
            nombre_tecnico: Nombre técnico del plugin
            
        Returns:
            Instancia del plugin o None si no está cargado
        """
        if nombre_tecnico in self.loaded_plugins:
            return self.loaded_plugins[nombre_tecnico]["instance"]
        return None
    
    def is_plugin_loaded(self, nombre_tecnico: str) -> bool:
        """Verificar si un plugin está cargado en memoria"""
        return nombre_tecnico in self.loaded_plugins
    
    def get_loaded_plugins(self) -> List[str]:
        """Obtener lista de plugins cargados"""
        return list(self.loaded_plugins.keys())
    
    def get_hook_subscribers(self, hook_name: str) -> List[Dict]:
        """Obtener lista de plugins suscritos a un hook"""
        return self.hooks.get(hook_name, [])


# Instancia global del PluginManager
plugin_manager = PluginManager()