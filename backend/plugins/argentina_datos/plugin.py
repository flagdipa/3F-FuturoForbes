from .services import ArgentinaDatosService
import logging
from typing import Dict, Any, List, Optional
from backend.plugins.base import BasePlugin

class ArgentinaDatosPlugin(BasePlugin):
    """
    Plugin para consumir datos financieros de api.argentinadatos.com
    Siguiendo la especificación detallada del prompt.
    """
    nombre_tecnico = "argentina_datos"
    nombre_display = "Argentina Datos"
    version = "1.1.0"
    autor = "3F Labs"
    descripcion = "Información financiera argentina: cotizaciones, inflación, UVA y más."
    hooks = ["daily_summary", "system_periodic_sync"]

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.service = ArgentinaDatosService()

    async def initialize(self):
        self.logger.info(f"{self.nombre_display} inicializado")
        # Asegurar que existan datos iniciales si no hay caché
        # El scheduler se encargará de las actualizaciones periódicas

    async def shutdown(self):
        self.logger.info(f"{self.nombre_display} apagado")

    async def sync_enabled_apis(self):
        """
        Sincroniza solo las APIs marcadas como 'activa' en la configuración.
        """
        apis = self.config.get("apis_disponibles", {})
        count = 0
        for key, api_config in apis.items():
            if api_config.get("activa", False):
                endpoint = api_config.get("endpoint")
                if endpoint:
                    self.logger.info(f"Sincronizando {key} ({endpoint})...")
                    await self.service.fetch_and_cache(endpoint)
                    count += 1
        return count

    async def get_active_data(self) -> Dict[str, Any]:
        """
        Retorna los datos de todas las APIs activas desde la caché.
        """
        apis = self.config.get("apis_disponibles", {})
        active_endpoints = [
            api_config["endpoint"] 
            for api_config in apis.values() 
            if api_config.get("activa", False) and "endpoint" in api_config
        ]
        return self.service.get_all_cached(active_endpoints)

    async def on_daily_summary(self, **kwargs):
        await self.sync_enabled_apis()

    async def on_system_periodic_sync(self, **kwargs):
        # El manager llamará a esto cada minuto, pero nosotros respetamos
        # el intervalo configurado de forma rudimentaria (o confiamos en la validez de la caché)
        # Aquí implementamos una verificación simple basada en el tiempo de la última sync general si fuera necesario,
        # pero fetch_and_cache en service ya maneja su propia lógica si quisiéramos.
        # Por ahora, simplemente llamamos al sync y dejamos que services decida si refrescar o no (o forzamos si el intervalo se cumple).
        await self.sync_enabled_apis()
