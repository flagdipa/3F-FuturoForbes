import aiohttp
from typing import Dict, Any, List
from backend.plugins.base import BasePlugin

class CryptoTrackerPlugin(BasePlugin):
    """
    Plugin to track live crypto prices using CoinGecko API.
    """
    technical_name = "crypto_tracker"
    display_name = "Crypto Live"
    version = "1.0.0"
    autor = "3F Labs"
    descripcion = "Seguimiento de precios de criptomonedas en tiempo real vía CoinGecko."
    hooks = ["dashboard_charts"]

    API_URL = "https://api.coingecko.com/api/v3/simple/price"

    async def initialize(self):
        self.logger.info(f"{self.display_name} inicializado")

    async def shutdown(self):
        self.logger.info(f"{self.display_name} apagado")

    async def get_live_prices(self, ids: List[str] = ["bitcoin", "ethereum", "tether", "binancecoin", "solana"]) -> Dict[str, Any]:
        """
        Fetch live prices from CoinGecko.
        """
        params = {
            "ids": ",".join(ids),
            "vs_currencies": "usd,ars",
            "include_24hr_change": "true"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.API_URL, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.error(f"Error API: {response.status}")
                        return {}
        except Exception as e:
            self.logger.error(f"Error fetching crypto prices: {e}")
            return {}
