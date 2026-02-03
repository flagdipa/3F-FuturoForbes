import configparser
import os
from typing import Dict, Any

class ConfigManager:
    """
    Gestor de configuración que lee archivos .inf (formato INI)
    para permitir la personalización del sistema sin tocar el código.
    """
    def __init__(self, config_dir: str = None):
        if config_dir is None:
            # Calcular ruta absoluta relativa a este archivo
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.config_dir = os.path.join(base_dir, "config")
        else:
            self.config_dir = config_dir
            
        self.config = configparser.ConfigParser()
        self._load_all_configs()

    def _load_all_configs(self):
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir, exist_ok=True)
            return

        for file in os.listdir(self.config_dir):
            if file.endswith(".inf"):
                self.config.read(os.path.join(self.config_dir, file), encoding='utf-8')

    def get(self, section: str, key: str, default: Any = None) -> Any:
        try:
            return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default

    def get_int(self, section: str, key: str, default: int = 0) -> int:
        try:
            return self.config.getint(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return default

    def get_bool(self, section: str, key: str, default: bool = False) -> bool:
        try:
            return self.config.getboolean(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return default

# Instancia global del gestor de configuración
config_inf = ConfigManager()
