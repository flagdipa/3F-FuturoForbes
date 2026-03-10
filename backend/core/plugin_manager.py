import os
import json
import importlib
import logging
from typing import List, Dict, Any, Optional
from sqlmodel import select

from .hooks_engine import dispatch_hook, register_hook

logger = logging.getLogger("plugin_manager")


def _get_plugin_model():
    """Lazy import to avoid circular dependencies."""
    from ..models import Plugin as PluginModel
    return PluginModel


def _get_base_plugin():
    """Lazy import to avoid circular dependencies."""
    from ..plugins.base import BasePlugin
    return BasePlugin


class PluginManager:
    """
    Manages the lifecycle of 3F plugins (PrestaShop style).
    Handles discovery, installation, configuration, and hooks.
    """

    def __init__(self, plugins_dir: str = None, db=None):
        self.plugins_dir = plugins_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "plugins"
        )
        self.db = db
        self.loaded_plugins: Dict[str, Any] = {}

    async def call_hook(self, hook_name: str, **kwargs) -> List[Any]:
        """Dispatch a hook to all registered listeners."""
        try:
            return await dispatch_hook(hook_name, **kwargs)
        except Exception as e:
            logger.warning(f"Hook '{hook_name}' failed silently: {e}")
            return []

    async def dispatch_hook(self, hook_name: str, **kwargs) -> List[Any]:
        """Alias for call_hook."""
        return await self.call_hook(hook_name, **kwargs)

    def discover_plugins(self) -> List[Dict[str, Any]]:
        """Scans the plugins directory for valid plugins."""
        found = []
        if not os.path.exists(self.plugins_dir):
            return found

        PluginModel = _get_plugin_model()

        for entry in os.scandir(self.plugins_dir):
            if entry.is_dir():
                manifest_path = os.path.join(entry.path, "plugin.json")
                if os.path.exists(manifest_path):
                    try:
                        with open(manifest_path, 'r') as f:
                            manifest = json.load(f)
                            manifest['id'] = entry.name

                            if self.db:
                                db_plugin = self.db.exec(select(PluginModel).where(PluginModel.nombre_tecnico == entry.name)).first()
                                manifest['is_installed'] = db_plugin is not None
                                manifest['is_active'] = db_plugin.activo if db_plugin else False
                            else:
                                manifest['is_installed'] = False
                                manifest['is_active'] = False

                            found.append(manifest)
                    except Exception as e:
                        logger.error(f"Error reading plugin manifest {entry.name}: {e}")
        return found

    def get_plugin_instance(self, plugin_id: str) -> Optional[Any]:
        """Dynamic load and instantiate a plugin class."""
        if plugin_id in self.loaded_plugins:
            return self.loaded_plugins[plugin_id]

        try:
            module_path = f"backend.plugins.{plugin_id}.plugin"
            module = importlib.import_module(module_path)
            plugin_class = getattr(module, "Plugin")

            default_config = {}
            if self.db:
                PluginModel = _get_plugin_model()
                db_plugin = self.db.exec(select(PluginModel).where(PluginModel.nombre_tecnico == plugin_id)).first()
                if db_plugin and db_plugin.configuracion:
                    default_config = db_plugin.configuracion

            instance = plugin_class(config=default_config)
            return instance
        except Exception as e:
            logger.error(f"Failed to instantiate plugin {plugin_id}: {e}")
            return None

    def install_plugin(self, plugin_id: str) -> bool:
        """Installs the plugin (runs DB schema changes and creates its row)."""
        if not self.db:
            return False

        PluginModel = _get_plugin_model()
        db_plugin = self.db.exec(select(PluginModel).where(PluginModel.nombre_tecnico == plugin_id)).first()
        if db_plugin:
            return True  # Already installed

        instance = self.get_plugin_instance(plugin_id)
        if not instance:
            return False

        try:
            if instance.install():
                db_plugin = PluginModel(
                    nombre_tecnico=plugin_id,
                    nombre_display=instance.name,
                    version=instance.version,
                    activo=False,
                    configuracion={}
                )
                self.db.add(db_plugin)
                self.db.commit()
                return True
        except Exception as e:
            logger.error(f"Error installing plugin {plugin_id}: {e}")
            self.db.rollback()
        return False

    def uninstall_plugin(self, plugin_id: str) -> bool:
        """Removes the plugin from DB."""
        if not self.db:
            return False

        PluginModel = _get_plugin_model()
        db_plugin = self.db.exec(select(PluginModel).where(PluginModel.nombre_tecnico == plugin_id)).first()
        if not db_plugin:
            return True

        self.deactivate_plugin(plugin_id)

        instance = self.get_plugin_instance(plugin_id)
        if instance:
            try:
                instance.uninstall()
            except Exception as e:
                logger.error(f"Error running uninstall on plugin {plugin_id}: {e}")

        self.db.delete(db_plugin)
        self.db.commit()
        return True

    def activate_plugin(self, plugin_id: str) -> bool:
        if not self.db:
            return False

        PluginModel = _get_plugin_model()
        db_plugin = self.db.exec(select(PluginModel).where(PluginModel.nombre_tecnico == plugin_id)).first()
        if not db_plugin:
            return False

        instance = self.get_plugin_instance(plugin_id)
        if not instance:
            return False

        if instance.activate():
            db_plugin.activo = True
            self.db.add(db_plugin)
            self.db.commit()

            self.loaded_plugins[plugin_id] = instance
            for attr_name in dir(instance):
                if attr_name.startswith("hook_"):
                    hook_name = attr_name.replace("hook_", "")
                    callback = getattr(instance, attr_name)
                    register_hook(hook_name, callback, plugin_id=plugin_id)
            return True
        return False

    def deactivate_plugin(self, plugin_id: str) -> bool:
        if not self.db:
            return False

        PluginModel = _get_plugin_model()
        db_plugin = self.db.exec(select(PluginModel).where(PluginModel.nombre_tecnico == plugin_id)).first()
        if not db_plugin:
            return False

        instance = self.loaded_plugins.get(plugin_id) or self.get_plugin_instance(plugin_id)
        if instance:
            instance.deactivate()

        db_plugin.activo = False
        self.db.add(db_plugin)
        self.db.commit()

        if plugin_id in self.loaded_plugins:
            del self.loaded_plugins[plugin_id]
        return True

    def get_active_plugins(self) -> List[Any]:
        return list(self.loaded_plugins.values())

    def get_plugin_config(self, plugin_id: str) -> dict:
        instance = self.get_plugin_instance(plugin_id)
        if instance:
            return instance.get_config()
        return {}

    def set_plugin_config(self, plugin_id: str, data: dict) -> bool:
        if not self.db:
            return False

        PluginModel = _get_plugin_model()
        db_plugin = self.db.exec(select(PluginModel).where(PluginModel.nombre_tecnico == plugin_id)).first()
        if not db_plugin:
            return False

        instance = self.get_plugin_instance(plugin_id)
        if instance and instance.set_config(data):
            db_plugin.configuracion = instance.get_config()
            self.db.add(db_plugin)
            self.db.commit()
            return True
        return False


# Singleton global instance (no DB - methods that need DB take it as param)
plugin_manager = PluginManager()
