"""
CriptoYa Multi-País Plugin - Cotizaciones de criptomonedas en Latinoamérica
Soporta 11 países: AR, BO, BR, CL, CO, DO, MX, PE, PY, UY, VE
"""
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from decimal import Decimal

from sqlmodel import Session, select, and_

from backend.plugins.base import BasePlugin
from backend.core.database import engine
from backend.models.models_criptoya import (
    CriptoYaConfig, CriptoYaPais, CriptoYaExchange,
    CriptoYaCoin, CriptoYaRate, CriptoYaFee
)


class CriptoYaMultiPlugin(BasePlugin):
    """
    Plugin para obtener cotizaciones de criptomonedas de CriptoYa API.
    Soporta múltiples países latinoamericanos y exchanges locales.
    """
    
    nombre_tecnico = "criptoya_multi"
    nombre_display = "CriptoYa Multi-País"
    version = "1.0.0"
    autor = "3F Team"
    descripcion = "Obtiene cotizaciones de criptomonedas de múltiples exchanges en Latinoamérica"
    hooks = ["daily_summary", "account_sync"]
    
    # Base URL de la API
    API_BASE_URL = "https://criptoya.com/api"
    
    # Países soportados
    PAISES_SOPORTADOS = {
        "AR": {"nombre": "Argentina", "moneda": "ARS", "nombre_display": "🇦🇷 Argentina"},
        "BO": {"nombre": "Bolivia", "moneda": "BOB", "nombre_display": "🇧🇴 Bolivia"},
        "BR": {"nombre": "Brazil", "moneda": "BRL", "nombre_display": "🇧🇷 Brazil"},
        "CL": {"nombre": "Chile", "moneda": "CLP", "nombre_display": "🇨🇱 Chile"},
        "CO": {"nombre": "Colombia", "moneda": "COP", "nombre_display": "🇨🇴 Colombia"},
        "DO": {"nombre": "República Dominicana", "moneda": "DOP", "nombre_display": "🇩🇴 República Dominicana"},
        "MX": {"nombre": "Mexico", "moneda": "MXN", "nombre_display": "🇲🇽 Mexico"},
        "PE": {"nombre": "Peru", "moneda": "PEN", "nombre_display": "🇵🇪 Peru"},
        "PY": {"nombre": "Paraguay", "moneda": "PYG", "nombre_display": "🇵🇾 Paraguay"},
        "UY": {"nombre": "Uruguay", "moneda": "UYU", "nombre_display": "🇺🇾 Uruguay"},
        "VE": {"nombre": "Venezuela", "moneda": "VES", "nombre_display": "🇻🇪 Venezuela"},
    }
    
    # Criptomonedas principales
    COINS_PRINCIPALES = [
        {"symbol": "BTC", "nombre": "Bitcoin", "tipo": "crypto", "popular": True},
        {"symbol": "ETH", "nombre": "Ethereum", "tipo": "crypto", "popular": True},
        {"symbol": "USDT", "nombre": "Tether", "tipo": "stablecoin", "popular": True},
        {"symbol": "USDC", "nombre": "USD Coin", "tipo": "stablecoin", "popular": True},
        {"symbol": "DAI", "nombre": "Dai", "tipo": "stablecoin", "popular": False},
        {"symbol": "SOL", "nombre": "Solana", "tipo": "crypto", "popular": True},
        {"symbol": "BNB", "nombre": "BNB", "tipo": "crypto", "popular": False},
        {"symbol": "XRP", "nombre": "XRP", "tipo": "crypto", "popular": False},
    ]
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_update: Optional[datetime] = None
    
    async def initialize(self):
        """Inicializar el plugin y preparar datos base"""
        self.logger.info(f"Inicializando {self.nombre_display}")
        
        # Crear sesión HTTP
        self.session = aiohttp.ClientSession(
            headers={"User-Agent": "3F-CriptoYa-Plugin/1.0"},
            timeout=aiohttp.ClientTimeout(total=30)
        )
        
        # Ensure tables are created
        from sqlmodel import SQLModel
        from backend.core.database import engine
        SQLModel.metadata.create_all(engine)
        
        # Inicializar datos base en la BD
        await self._inicializar_datos_base()
        
        self.logger.info(f"✅ {self.nombre_display} inicializado correctamente")
        self.logger.info(f"   Países soportados: {len(self.PAISES_SOPORTADOS)}")
        self.logger.info(f"   Coins principales: {len(self.COINS_PRINCIPALES)}")
    
    async def shutdown(self):
        """Cerrar el plugin"""
        self.logger.info(f"Apagando {self.nombre_display}")
        if self.session:
            await self.session.close()
            self.session = None
    
    async def on_daily_summary(self, user, summary):
        """
        Hook ejecutado en el resumen diario.
        Actualiza cotizaciones para usuarios con auto_update habilitado.
        """
        if not self.get_config("enabled", True):
            return
        
        # Verificar si toca actualizar
        intervalo = self.get_config("update_interval_minutes", 5)
        if self.last_update and (datetime.now() - self.last_update).seconds < (intervalo * 60):
            return
        
        self.logger.info("🔄 Actualizando cotizaciones CriptoYa...")
        await self.actualizar_todas_las_cotizaciones()
        self.last_update = datetime.now()
    
    async def on_account_sync(self, account, transactions):
        """
        Hook para sincronización de cuentas.
        Puede actualizar cotizaciones si la cuenta es de cripto.
        """
        # Verificar si la cuenta está relacionada con cripto
        # Esta función puede expandirse según necesidades
        pass
    
    async def _inicializar_datos_base(self):
        """Inicializar países y coins en la base de datos"""
        session = Session(engine)
        
        try:
            # Inicializar países
            for codigo, datos in self.PAISES_SOPORTADOS.items():
                existing = session.exec(
                    select(CriptoYaPais).where(CriptoYaPais.codigo_iso == codigo)
                ).first()
                
                if not existing:
                    pais = CriptoYaPais(
                        codigo_iso=codigo,
                        nombre=datos["nombre"],
                        nombre_display=datos["nombre_display"],
                        moneda_local=datos["moneda"],
                        disponible=True,
                        requiere_volumen=True
                    )
                    session.add(pais)
                    self.logger.debug(f"País agregado: {codigo}")
            
            # Inicializar coins
            for coin_data in self.COINS_PRINCIPALES:
                existing = session.exec(
                    select(CriptoYaCoin).where(CriptoYaCoin.symbol == coin_data["symbol"])
                ).first()
                
                if not existing:
                    coin = CriptoYaCoin(
                        symbol=coin_data["symbol"],
                        nombre=coin_data["nombre"],
                        tipo=coin_data["tipo"],
                        popular=coin_data["popular"],
                        activo=True
                    )
                    session.add(coin)
                    self.logger.debug(f"Coin agregado: {coin_data['symbol']}")
            
            session.commit()
            self.logger.info("✅ Datos base inicializados")
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error inicializando datos base: {e}")
        finally:
            session.close()
    
    async def actualizar_todas_las_cotizaciones(self):
        """Actualizar cotizaciones para todos los países y coins configurados"""
        paises = self.get_config("paises", ["AR"])  # Default Argentina
        coins = self.get_config("coins", ["BTC", "ETH", "USDT"])
        volumen = self.get_config("volumen_default", 0.1)
        
        for pais_codigo in paises:
            if pais_codigo not in self.PAISES_SOPORTADOS:
                continue
            
            moneda = self.PAISES_SOPORTADOS[pais_codigo]["moneda"]
            
            for coin in coins:
                try:
                    await self.obtener_cotizacion_general(pais_codigo, coin, moneda, volumen)
                except Exception as e:
                    self.logger.error(f"Error obteniendo {coin}/{moneda} para {pais_codigo}: {e}")
    
    async def obtener_cotizacion_general(
        self, 
        pais_codigo: str, 
        coin: str, 
        fiat: str, 
        volumen: float = 0.1
    ) -> List[Dict[str, Any]]:
        """
        Obtener cotización general de todos los exchanges para un par coin/fiat.
        
        Args:
            pais_codigo: Código ISO del país (AR, BR, CL, etc.)
            coin: Símbolo de la criptomoneda (BTC, ETH, etc.)
            fiat: Código de moneda fiat (ARS, BRL, etc.)
            volumen: Volumen a operar
            
        Returns:
            Lista de cotizaciones por exchange
        """
        if not self.session:
            raise RuntimeError("Plugin no inicializado")
        
        url = f"{self.API_BASE_URL}/{coin}/{fiat}/{volumen}"
        
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    self.logger.error(f"Error API: {response.status} para {url}")
                    return []
                
                data = await response.json()
                
                # Procesar y guardar cotizaciones
                await self._guardar_cotizaciones(pais_codigo, coin, fiat, volumen, data)
                
                return data
                
        except Exception as e:
            self.logger.error(f"Error consultando API: {e}")
            return []
    
    async def _guardar_cotizaciones(
        self, 
        pais_codigo: str, 
        coin: str, 
        fiat: str, 
        volumen: float,
        data: Dict[str, Any]
    ):
        """Guardar cotizaciones en la base de datos"""
        session = Session(engine)
        
        try:
            # Obtener IDs
            pais = session.exec(
                select(CriptoYaPais).where(CriptoYaPais.codigo_iso == pais_codigo)
            ).first()
            
            coin_obj = session.exec(
                select(CriptoYaCoin).where(CriptoYaCoin.symbol == coin)
            ).first()
            
            if not pais or not coin_obj:
                self.logger.warning(f"País o coin no encontrado: {pais_codigo}/{coin}")
                return
            
            for exchange_slug, cotizacion in data.items():
                if not isinstance(cotizacion, dict):
                    continue
                
                # Buscar o crear exchange
                exchange = session.exec(
                    select(CriptoYaExchange).where(
                        and_(
                            CriptoYaExchange.slug == exchange_slug,
                            CriptoYaExchange.id_pais == pais.id_pais
                        )
                    )
                ).first()
                
                if not exchange:
                    exchange = CriptoYaExchange(
                        id_pais=pais.id_pais,
                        slug=exchange_slug,
                        nombre=exchange_slug.replace("_", " ").title(),
                        activo=True
                    )
                    session.add(exchange)
                    session.flush()
                
                # Calcular spread
                ask = Decimal(str(cotizacion.get("ask", 0)))
                bid = Decimal(str(cotizacion.get("bid", 0)))
                spread = ask - bid
                spread_pct = (spread / bid * 100) if bid > 0 else Decimal("0")
                
                # Crear registro de cotización
                rate = CriptoYaRate(
                    id_pais=pais.id_pais,
                    id_exchange=exchange.id_exchange,
                    id_coin=coin_obj.id_coin,
                    fiat=fiat,
                    ask=ask,
                    total_ask=Decimal(str(cotizacion.get("totalAsk", 0))),
                    bid=bid,
                    total_bid=Decimal(str(cotizacion.get("totalBid", 0))),
                    volumen=Decimal(str(volumen)),
                    spread=spread,
                    spread_porcentaje=spread_pct,
                    timestamp_api=cotizacion.get("time", 0)
                )
                session.add(rate)
            
            session.commit()
            self.logger.debug(f"✅ Cotizaciones guardadas: {coin}/{fiat} en {pais_codigo}")
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error guardando cotizaciones: {e}")
        finally:
            session.close()
    
    async def obtener_comisiones(self, pais_codigo: str) -> Dict[str, Any]:
        """
        Obtener comisiones de retiro para un país.
        
        Args:
            pais_codigo: Código ISO del país
            
        Returns:
            Diccionario con comisiones por exchange
        """
        if not self.session:
            raise RuntimeError("Plugin no inicializado")
        
        # Nota: El endpoint de fees es global, no por país
        url = f"{self.API_BASE_URL}/fees"
        
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    return {}
                
                data = await response.json()
                await self._guardar_comisiones(pais_codigo, data)
                return data
                
        except Exception as e:
            self.logger.error(f"Error obteniendo comisiones: {e}")
            return {}
    
    async def _guardar_comisiones(self, pais_codigo: str, data: Dict[str, Any]):
        """Guardar comisiones en la base de datos"""
        session = Session(engine)
        
        try:
            pais = session.exec(
                select(CriptoYaPais).where(CriptoYaPais.codigo_iso == pais_codigo)
            ).first()
            
            if not pais:
                return
            
            for exchange_slug, coins_data in data.items():
                # Buscar exchange
                exchange = session.exec(
                    select(CriptoYaExchange).where(
                        and_(
                            CriptoYaExchange.slug == exchange_slug,
                            CriptoYaExchange.id_pais == pais.id_pais
                        )
                    )
                ).first()
                
                if not exchange:
                    continue
                
                for coin_symbol, redes in coins_data.items():
                    coin = session.exec(
                        select(CriptoYaCoin).where(CriptoYaCoin.symbol == coin_symbol)
                    ).first()
                    
                    if not coin:
                        continue
                    
                    for red, fee_data in redes.items():
                        # Buscar si ya existe fee
                        existing = session.exec(
                            select(CriptoYaFee).where(
                                and_(
                                    CriptoYaFee.id_exchange == exchange.id_exchange,
                                    CriptoYaFee.id_coin == coin.id_coin,
                                    CriptoYaFee.red == red
                                )
                            )
                        ).first()
                        
                        if existing:
                            # Actualizar
                            existing.comision = Decimal(str(fee_data.get("fee", 0)))
                            existing.activo = True
                            existing.actualizado_el = datetime.now()
                        else:
                            # Crear nuevo
                            fee = CriptoYaFee(
                                id_exchange=exchange.id_exchange,
                                id_coin=coin.id_coin,
                                red=red,
                                comision=Decimal(str(fee_data.get("fee", 0))),
                                activo=True
                            )
                            session.add(fee)
            
            session.commit()
            self.logger.info(f"✅ Comisiones actualizadas para {pais_codigo}")
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error guardando comisiones: {e}")
        finally:
            session.close()
    
    def obtener_mejor_precio(
        self, 
        pais_codigo: str, 
        coin: str, 
        fiat: str, 
        tipo: str = "compra"
    ) -> Optional[Dict[str, Any]]:
        """
        Obtener el mejor precio disponible para un par.
        
        Args:
            pais_codigo: Código ISO del país
            coin: Símbolo de la criptomoneda
            fiat: Código de moneda fiat
            tipo: 'compra' (menor ask) o 'venta' (mayor bid)
            
        Returns:
            Diccionario con información del mejor precio o None
        """
        session = Session(engine)
        
        try:
            # Obtener últimas cotizaciones (últimos 5 minutos)
            desde = datetime.now() - timedelta(minutes=5)
            
            query = select(CriptoYaRate).join(CriptoYaPais).join(CriptoYaCoin).where(
                and_(
                    CriptoYaPais.codigo_iso == pais_codigo,
                    CriptoYaCoin.symbol == coin,
                    CriptoYaRate.fiat == fiat,
                    CriptoYaRate.creado_el >= desde
                )
            )
            
            rates = session.exec(query).all()
            
            if not rates:
                return None
            
            if tipo == "compra":
                # Buscar menor ask (mejor precio para comprar)
                mejor = min(rates, key=lambda r: r.ask)
            else:
                # Buscar mayor bid (mejor precio para vender)
                mejor = max(rates, key=lambda r: r.bid)
            
            return {
                "exchange": mejor.exchange.nombre if mejor.exchange else None,
                "ask": float(mejor.ask),
                "bid": float(mejor.bid),
                "spread": float(mejor.spread),
                "spread_porcentaje": float(mejor.spread_porcentaje),
                "timestamp": mejor.timestamp_api
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo mejor precio: {e}")
            return None
        finally:
            session.close()
    
    async def crear_alerta(
        self, 
        user_id: int,
        coin: str, 
        pais_codigo: str, 
        fiat: str,
        tipo: str,
        valor: float
    ) -> bool:
        """
        Crear una alerta de precio.
        
        Args:
            user_id: ID del usuario
            coin: Símbolo de la criptomoneda
            pais_codigo: Código ISO del país
            fiat: Moneda fiat
            tipo: 'mayor_que', 'menor_que'
            valor: Valor objetivo
            
        Returns:
            True si se creó exitosamente
        """
        # Esta función se puede expandir para crear alertas en la BD
        # y notificar cuando se cumplan las condiciones
        self.logger.info(f"Alerta creada: {user_id} - {coin}/{fiat} {tipo} {valor}")
        return True
    
    def get_estadisticas(self, pais_codigo: str = None) -> Dict[str, Any]:
        """
        Obtener estadísticas del plugin.
        
        Args:
            pais_codigo: Filtrar por país (opcional)
            
        Returns:
            Diccionario con estadísticas
        """
        session = Session(engine)
        
        try:
            stats = {
                "total_paises": session.exec(select(CriptoYaPais)).all().__len__(),
                "total_exchanges": session.exec(select(CriptoYaExchange)).all().__len__(),
                "total_coins": session.exec(select(CriptoYaCoin)).all().__len__(),
                "total_rates_24h": 0,
                "paises_activos": []
            }
            
            # Contar rates de últimas 24 horas
            desde = datetime.now() - timedelta(hours=24)
            rates_query = select(CriptoYaRate).where(CriptoYaRate.creado_el >= desde)
            if pais_codigo:
                rates_query = rates_query.join(CriptoYaPais).where(
                    CriptoYaPais.codigo_iso == pais_codigo
                )
            
            stats["total_rates_24h"] = session.exec(rates_query).all().__len__()
            
            # Países con actividad reciente
            paises_activos = session.exec(
                select(CriptoYaPais.codigo_iso)
                .join(CriptoYaRate)
                .where(CriptoYaRate.creado_el >= desde)
                .distinct()
            ).all()
            stats["paises_activos"] = [p for p in paises_activos]
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
        finally:
            session.close()
