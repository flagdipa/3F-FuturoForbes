"""
Dolar Hoy Plugin - Actualiza tasas de cambio del dólar en Argentina
"""
import aiohttp
from typing import Dict, Any
from datetime import datetime
from sqlmodel import Session, select
from backend.plugins.base import BasePlugin
from backend.core.database import engine
from backend.models.models import Divisa, HistorialDivisa


class DolarHoyPlugin(BasePlugin):
    """
    Plugin para actualizar automáticamente las cotizaciones del dólar en Argentina.
    Soporta: Dólar Blue, MEP (Bolsa), CCL (Contado con Liqui), Cripto.
    """
    
    nombre_tecnico = "dolar_hoy"
    nombre_display = "Dólar Hoy Argentina"
    version = "1.0.0"
    autor = "3F Team"
    descripcion = "Actualiza automáticamente las cotizaciones del dólar (Blue, MEP, CCL, Cripto)"
    hooks = ["daily_summary"]
    
    # URLs de APIs para cotizaciones
    API_URLS = {
        "blue": "https://dolarapi.com/v1/dolares/blue",
        "mep": "https://dolarapi.com/v1/dolares/bolsa",
        "ccl": "https://dolarapi.com/v1/dolares/contadoconliqui",
        "cripto": "https://dolarapi.com/v1/dolares/cripto"
    }
    
    async def initialize(self):
        """Inicializar el plugin"""
        self.logger.info(f"Inicializando {self.nombre_display}")
        
        # Configurar defaults
        if "sources" not in self.config:
            self.config["sources"] = ["blue", "mep", "ccl"]
        
        if "update_frequency" not in self.config:
            self.config["update_frequency"] = "hourly"
        
        if "create_divisas_if_missing" not in self.config:
            self.config["create_divisas_if_missing"] = True
        
        self.logger.info(f"✅ {self.nombre_display} inicializado")
        self.logger.info(f"Fuentes configuradas: {self.config['sources']}")
    
    async def shutdown(self):
        """Cerrar el plugin"""
        self.logger.info(f"Apagando {self.nombre_display}")
    
    async def on_daily_summary(self, user, summary):
        """
        Actualizar tasas en el resumen diario.
        También se puede usar un hook de schedule específico.
        """
        await self.update_exchange_rates()
    
    async def update_exchange_rates(self):
        """
        Actualizar todas las tasas de cambio configuradas.
        Este método puede ser llamado manualmente o por un hook.
        """
        self.logger.info("Actualizando tasas de cambio...")
        
        session = Session(engine)
        try:
            for source in self.config["sources"]:
                if source not in self.API_URLS:
                    self.logger.warning(f"Fuente desconocida: {source}")
                    continue
                
                try:
                    await self._update_rate(source, session)
                except Exception as e:
                    self.logger.error(f"Error actualizando {source}: {e}")
                    continue
            
            session.commit()
            self.logger.info("✅ Tasas actualizadas correctamente")
            
        finally:
            session.close()
    
    async def _update_rate(self, source: str, session: Session):
        """
        Actualizar una tasa específica.
        
        Args:
            source: Nombre de la fuente (blue, mep, ccl, cripto)
            session: Sesión de base de datos
        """
        url = self.API_URLS[source]
        
        async with aiohttp.ClientSession() as http_session:
            async with http_session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}")
                
                data = await response.json()
                
                # Extraer datos
                compra = data.get("compra", 0)
                venta = data.get("venta", 0)
                promedio = (compra + venta) / 2 if compra and venta else (compra or venta)
                fecha_actualizacion = data.get("fechaActualizacion", datetime.now().isoformat())
                
                # Determinar código ISO según la fuente
                codigo_iso_map = {
                    "blue": "USD_BLUE",
                    "mep": "USD_MEP",
                    "ccl": "USD_CCL",
                    "cripto": "USD_CRIPTO"
                }
                
                codigo_iso = codigo_iso_map.get(source)
                
                # Buscar o crear divisa
                divisa = session.exec(
                    select(Divisa).where(Divisa.codigo_iso == codigo_iso)
                ).first()
                
                if not divisa:
                    if self.config.get("create_divisas_if_missing", True):
                        # Crear nueva divisa
                        nombre_map = {
                            "blue": "Dólar Blue",
                            "mep": "Dólar MEP",
                            "ccl": "Dólar CCL",
                            "cripto": "Dólar Cripto"
                        }
                        
                        divisa = Divisa(
                            nombre_divisa=nombre_map.get(source, f"USD {source.upper()}"),
                            codigo_iso=codigo_iso,
                            simbolo_prefijo="$",
                            tipo_divisa="Fiat",
                            decimal_places=2,
                            tasa_conversion_base=promedio
                        )
                        session.add(divisa)
                        session.flush()
                        self.logger.info(f"Divisa {codigo_iso} creada")
                    else:
                        self.logger.warning(f"Divisa {codigo_iso} no encontrada")
                        return
                else:
                    # Actualizar tasa
                    divisa.tasa_conversion_base = promedio
                    session.add(divisa)
                
                # Crear registro en historial
                historial = HistorialDivisa(
                    id_divisa=divisa.id_divisa,
                    fecha_tasa=datetime.now().date(),
                    tasa_valor=promedio,
                    tipo_actualizacion=1  # 1 = Automático
                )
                session.add(historial)
                
                self.logger.debug(f"{source}: ${promedio}")
    
    async def get_current_rates(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtener las tasas actuales sin guardar en BD.
        Útil para mostrar en el frontend.
        
        Returns:
            Diccionario con tasas por fuente
        """
        rates = {}
        
        for source in self.config["sources"]:
            if source not in self.API_URLS:
                continue
            
            try:
                url = self.API_URLS[source]
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            rates[source] = {
                                "compra": data.get("compra"),
                                "venta": data.get("venta"),
                                "fecha": data.get("fechaActualizacion"),
                                "casa": data.get("casa")
                            }
            except Exception as e:
                self.logger.error(f"Error obteniendo {source}: {e}")
                rates[source] = {"error": str(e)}
        
        return rates
    
    def get_supported_sources(self) -> list:
        """Obtener lista de fuentes soportadas"""
        return list(self.API_URLS.keys())
