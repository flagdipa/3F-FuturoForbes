import httpx
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from decimal import Decimal

logger = logging.getLogger(__name__)

class FXService:
    def __init__(self):
        self.cache: Dict[str, Dict] = {}
        self.cache_duration = timedelta(hours=1)
        # Using public APIs for Argentina (DolarApi) and Crypto (CoinGecko/Binance)
        self.DOLAR_API_URL = "https://dolarapi.com/v1/dolares"
        self.CRYPTO_API_URL = "https://api.binance.com/api/v3/ticker/price"

    async def get_rates(self) -> Dict[str, float]:
        """
        Returns latest exchange rates with caching.
        Base is ARS (how many ARS for 1 unit of foreign currency).
        """
        now = datetime.utcnow()
        if "rates" in self.cache and (now - self.cache["rates"]["timestamp"]) < self.cache_duration:
            return self.cache["rates"]["data"]

        rates = {
            "ARS": 1.0,
            "USD_OFFICIAL": 1000.0, # Fallbacks
            "USD_BLUE": 1200.0,
            "BTC": 90000000.0,
            "ETH": 3000000.0
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 1. Fetch ARS Dolar Rates
                dolar_res = await client.get(self.DOLAR_API_URL)
                if dolar_res.status_code == 200:
                    dolar_data = dolar_res.json()
                    for item in dolar_data:
                        if item["casa"] == "oficial":
                            rates["USD_OFFICIAL"] = float(item["venta"])
                        if item["casa"] == "blue":
                            rates["USD_BLUE"] = float(item["venta"])
                
                # 2. Fetch Crypto Prices (in USD)
                crypto_params = {"symbols": '["BTCUSDT","ETHUSDT"]'}
                crypto_res = await client.get(self.CRYPTO_API_URL, params=crypto_params)
                if crypto_res.status_code == 200:
                    crypto_data = crypto_res.json()
                    for item in crypto_data:
                        symbol = item["symbol"].replace("USDT", "")
                        price_usd = float(item["price"])
                        # Convert to ARS Blue
                        rates[symbol] = price_usd * rates["USD_BLUE"]

            self.cache["rates"] = {
                "timestamp": now,
                "data": rates
            }
            logger.info("FX Rates updated successfully")
            return rates

        except Exception as e:
            logger.error(f"Error updating FX rates: {e}")
            return self.cache.get("rates", {}).get("data", rates)

    def convert(self, amount: Decimal, from_curr: str, to_curr: str, rates: Dict[str, float]) -> Decimal:
        """
        Synchronic conversion helper using provided rates.
        Rates are assumed to be ARS-based (1 unit = X ARS).
        """
        if from_curr == to_curr:
            return amount

        # Convert to ARS first (base)
        # Handle special names for USD
        f_rate = rates.get(from_curr, rates.get("USD_BLUE") if "USD" in from_curr else 1.0)
        t_rate = rates.get(to_curr, rates.get("USD_BLUE") if "USD" in to_curr else 1.0)

        ars_value = Decimal(str(amount)) * Decimal(str(f_rate))
        return ars_value / Decimal(str(t_rate))

fx_service = FXService()
