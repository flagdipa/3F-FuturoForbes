from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from backend.api.auth.deps import get_current_user
from backend.core.plugin_manager import plugin_manager

router = APIRouter(prefix="/market", tags=["Market Data"], dependencies=[Depends(get_current_user)])

@router.get("/dolar-hoy")
async def get_dolar_hoy():
    plugin = plugin_manager.get_plugin_instance("dolar_hoy")
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin Dolar Hoy no está activo")
    
    try:
        return await plugin.get_current_rates()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/criptoya/mejor-precio")
async def get_criptoya_mejor_precio(coin: str = "BTC", fiat: str = "ARS", tipo: str = "compra"):
    plugin = plugin_manager.get_plugin_instance("criptoya_multi")
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin CriptoYa no está activo")
    
    try:
        # CriptoYa multi defaults to ARS for many things but let's be explicit
        res = plugin.obtener_mejor_precio("AR", coin, fiat, tipo)
        if not res:
            return {"error": "No hay datos recientes"}
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/criptoya/stats")
async def get_criptoya_stats():
    plugin = plugin_manager.get_plugin_instance("criptoya_multi")
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin CriptoYa no está activo")
    
    try:
        return plugin.get_estadisticas()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/crypto-live")
async def get_crypto_live():
    plugin = plugin_manager.get_plugin_instance("crypto_tracker")
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin Crypto Live no está activo")
    
    try:
        return await plugin.get_live_prices()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/argentina/cotizaciones")
async def get_arg_cotizaciones():
    plugin = plugin_manager.get_plugin_instance("argentina_datos")
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin Argentina Datos no está activo")
    return await plugin.get_cotizaciones()

@router.get("/argentina/inflacion")
async def get_arg_inflacion():
    plugin = plugin_manager.get_plugin_instance("argentina_datos")
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin Argentina Datos no está activo")
    return await plugin.get_inflacion()

@router.get("/billeteras/comparativa")
async def get_billeteras_comparativa():
    plugin = plugin_manager.get_plugin_instance("cuentas_wallet")
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin Cuentas / Billetera no está activo")
    return await plugin.get_comparison_data()
