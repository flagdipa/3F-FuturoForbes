import httpx
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from ..base import BasePlugin

logger = logging.getLogger("plugin_cotizaciones")

class Plugin(BasePlugin):
    """
    Plugin unificado de cotizaciones para Argentina y Latam.
    Consume Bluelytics, Ámbito y CriptoYa.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.update_interval = config.get("update_interval", 300) # 5 min
        self._cache = {}
        self._last_update = None

    async def on_enable(self):
        logger.info("Plugin Cotizaciones Latam habilitado.")
        # Programar primera actualización
        asyncio.create_task(self._refresh_loop())

    async def _refresh_loop(self):
        while self.is_active:
            try:
                await self.update_rates()
            except Exception as e:
                logger.error(f"Error actualizando cotizaciones: {e}")
            await asyncio.sleep(self.update_interval)

    async def update_rates(self):
        """Fetch rates from multiple sources."""
        results = {}
        
        async with httpx.AsyncClient(timeout=10) as client:
            # 1. Bluelytics (Blue/Oficial ARS)
            try:
                r = await client.get("https://api.bluelytics.com.ar/v2/latest")
                data = r.json()
                results['ars_blue'] = data['blue']
                results['ars_oficial'] = data['oficial']
            except: logger.warning("Fallo Bluelytics")

            # 2. CriptoYa (MEP, CCL, BTC, USDT)
            try:
                # MEP ARS via CriptoYa
                r = await client.get("https://criptoya.com/api/dolar")
                data = r.json()
                results['ars_mep'] = data['mep']['al30']['48h']['price']
            except: logger.warning("Fallo CriptoYa MEP")
            
            # 3. BTC/USD via CriptoYa
            try:
                r = await client.get("https://criptoya.com/api/binance/btc/usdt/1.0")
                results['btc_usd'] = r.json()['ask']
            except: logger.warning("Fallo CriptoYa BTC")

        self._cache = results
        self._last_update = datetime.now()
        logger.info(f"Cotizaciones actualizadas: {list(results.keys())}")

    # --- Hooks ---

    async def hook_displayDashboardTop(self, params: Dict[str, Any]) -> str:
        """Injects a horizontal ticker in the dashboard top hook."""
        if not self._cache:
            return ""
            
        blue = self._cache.get('ars_blue', {}).get('value_sell', '?')
        mep = self._cache.get('ars_mep', '?')
        btc = f"{self._cache.get('btc_usd', 0):,.0f}"
        
        html = f"""
        <div class="cotizaciones-ticker d-flex gap-4 small font-orbitron py-1 px-3 bg-black bg-opacity-50 border-bottom border-primary border-opacity-10">
            <div class="ticker-item"><span class="text-dim">USD BLUE:</span> <span class="text-success">${blue}</span></div>
            <div class="ticker-item"><span class="text-dim">USD MEP:</span> <span class="text-info">${mep}</span></div>
            <div class="ticker-item"><span class="text-dim">BTC/USD:</span> <span class="text-warning">${btc}</span></div>
        </div>
        <style>
            .cotizaciones-ticker {{ letter-spacing: 1px; font-size: 0.65rem; }}
        </style>
        """
        return html

    async def hook_actionDailySummary(self, user_data: Dict[str, Any]):
        """Injects data into the daily summary email/notification."""
        return {
            "cotizaciones": self._cache,
            "timestamp": self._last_update.isoformat() if self._last_update else None
        }
