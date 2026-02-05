from fastapi import APIRouter, Depends
from ...core.fx_service import fx_service

router = APIRouter(prefix="/fx", tags=["Forex Intelligence"])

@router.get("/rates")
async def get_exchange_rates():
    """
    Returns current exchange rates (conversion to ARS).
    """
    rates = await fx_service.get_rates()
    return {
        "rates": rates,
        "base": "ARS",
        "timestamp": fx_service.cache.get("rates", {}).get("timestamp", "")
    }
