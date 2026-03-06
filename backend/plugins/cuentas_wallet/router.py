"""
Router — Plugin Cuentas / Billetera
Endpoints REST para gestión de tasas de wallets y fintechs.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlmodel import Session, SQLModel
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

from backend.core.database import get_session

router = APIRouter(prefix="/cuentas-wallet", tags=["Cuentas / Billetera"])


def _get_services():
    from backend.plugins.cuentas_wallet.services import (
        EntidadService, TasaService, ComparadorService, SyncService
    )
    return EntidadService, TasaService, ComparadorService, SyncService


# ─── Entidades ────────────────────────────────────────────────────────────────

@router.get("/entidades", summary="Listar wallets y fintechs")
def listar_entidades(
    solo_activas: bool = Query(True),
    session: Session = Depends(get_session),
):
    EntidadService, *_ = _get_services()
    return EntidadService.listar(session, solo_activas)


@router.post("/entidades", summary="Crear wallet/fintech", status_code=201)
def crear_entidad(data: dict, session: Session = Depends(get_session)):
    EntidadService, *_ = _get_services()
    return EntidadService.crear(session, data)


@router.get("/entidades/{id}", summary="Detalle de una entidad")
def obtener_entidad(id: int, session: Session = Depends(get_session)):
    EntidadService, *_ = _get_services()
    ent = EntidadService.obtener(session, id)
    if not ent:
        raise HTTPException(status_code=404, detail="Entidad no encontrada")
    return ent


@router.put("/entidades/{id}", summary="Actualizar entidad")
def actualizar_entidad(id: int, data: dict, session: Session = Depends(get_session)):
    EntidadService, *_ = _get_services()
    ent = EntidadService.actualizar(session, id, data)
    if not ent:
        raise HTTPException(status_code=404, detail="Entidad no encontrada")
    return ent


@router.delete("/entidades/{id}", summary="Desactivar entidad")
def eliminar_entidad(id: int, session: Session = Depends(get_session)):
    EntidadService, *_ = _get_services()
    ok = EntidadService.eliminar(session, id)
    if not ok:
        raise HTTPException(status_code=404, detail="Entidad no encontrada")
    return {"mensaje": "Entidad desactivada"}


# ─── Tasas ────────────────────────────────────────────────────────────────────

@router.get("/tasas", summary="Listar tasas de interés")
def listar_tasas(
    id_entidad: Optional[int] = Query(None),
    moneda: Optional[str] = Query(None),
    solo_activas: bool = Query(True),
    session: Session = Depends(get_session),
):
    _, TasaService, *_ = _get_services()
    return TasaService.listar(session, id_entidad, moneda, solo_activas)


@router.post("/tasas", summary="Registrar tasa", status_code=201)
def crear_tasa(data: dict, session: Session = Depends(get_session)):
    _, TasaService, *_ = _get_services()
    return TasaService.crear(session, data)


@router.put("/tasas/{id}", summary="Actualizar tasa (genera historial automático)")
def actualizar_tasa(id: int, data: dict, session: Session = Depends(get_session)):
    _, TasaService, *_ = _get_services()
    tasa = TasaService.actualizar(session, id, data)
    if not tasa:
        raise HTTPException(status_code=404, detail="Tasa no encontrada")
    return tasa


@router.delete("/tasas/{id}", summary="Desactivar tasa")
def eliminar_tasa(id: int, session: Session = Depends(get_session)):
    _, TasaService, *_ = _get_services()
    ok = TasaService.eliminar(session, id)
    if not ok:
        raise HTTPException(status_code=404, detail="Tasa no encontrada")
    return {"mensaje": "Tasa desactivada"}


# ─── Comparador ───────────────────────────────────────────────────────────────

@router.get("/comparar", summary="Comparar tasas entre entidades (ranking)")
def comparar_tasas(
    moneda: str = Query("ARS", description="Moneda: ARS | USDT | DAI | USD"),
    tipo_producto: Optional[str] = Query(
        None, description="Filtrar por producto: Plazo Fijo | Cuenta Remunerada | FCI"
    ),
    session: Session = Depends(get_session),
):
    """
    Retorna ranking de tasas ordenado de mayor a menor,
    enriquecido con información de la entidad.
    """
    _, _, ComparadorService, _ = _get_services()
    return ComparadorService.comparar(session, moneda, tipo_producto)


@router.get("/entidades/{id}/historial", summary="Historial de tasas de una entidad")
def historial_entidad(
    id: int,
    limite: int = Query(30, ge=1, le=200),
    session: Session = Depends(get_session),
):
    _, _, ComparadorService, _ = _get_services()
    return ComparadorService.historial_entidad(session, id, limite)


# ─── Sincronización automática ────────────────────────────────────────────────

@router.post("/sincronizar", summary="Sincronizar tasas desde APIs públicas")
async def sincronizar(
    background_tasks: BackgroundTasks,
    fuente: str = Query("plazo_fijo", description="Fuente: plazo_fijo"),
    session: Session = Depends(get_session),
):
    """
    Sincroniza tasas desde argentinadatos.com en segundo plano.
    Actualmente soporta: `plazo_fijo`.
    """
    _, _, _, SyncService = _get_services()
    if fuente == "plazo_fijo":
        background_tasks.add_task(SyncService.sincronizar_plazo_fijo, session)
        return {"mensaje": "Sincronización iniciada en segundo plano", "fuente": fuente}
    raise HTTPException(status_code=400, detail=f"Fuente desconocida: {fuente}")


@router.post("/seed", summary="Cargar entidades de ejemplo", status_code=201)
def seed_entidades(session: Session = Depends(get_session)):
    """Carga un conjunto de wallets/fintechs argentinas de ejemplo."""
    EntidadService, TasaService, *_ = _get_services()
    from backend.plugins.cuentas_wallet.models import MonedaTasa, FuenteDato

    entidades_ejemplo = [
        {"nombre": "Mercado Pago", "nombre_corto": "MP", "tipo": "Billetera Virtual",
         "color_hex": "#009EE3", "url_web": "https://mercadopago.com.ar"},
        {"nombre": "Uala", "nombre_corto": "Uala", "tipo": "Billetera Virtual",
         "color_hex": "#7B2FBE"},
        {"nombre": "Lemon Cash", "nombre_corto": "Lemon", "tipo": "Fintech Crypto",
         "color_hex": "#F5FF67"},
        {"nombre": "Buenbit", "nombre_corto": "Buenbit", "tipo": "Exchange Crypto",
         "color_hex": "#FF6B2B"},
        {"nombre": "Naranja X", "nombre_corto": "NX", "tipo": "Fintech",
         "color_hex": "#FF7900"},
        {"nombre": "Personal Pay", "nombre_corto": "PP", "tipo": "Billetera Virtual",
         "color_hex": "#001489"},
        {"nombre": "Banco Nación", "nombre_corto": "BNA", "tipo": "Banco",
         "color_hex": "#007AC3"},
        {"nombre": "Banco Galicia", "nombre_corto": "Galicia", "tipo": "Banco",
         "color_hex": "#E4202A"},
    ]

    creadas = 0
    for datos in entidades_ejemplo:
        from backend.plugins.cuentas_wallet.models import CuentasWalletEntidad
        from sqlmodel import select
        existe = session.exec(
            select(CuentasWalletEntidad).where(
                CuentasWalletEntidad.nombre == datos["nombre"]
            )
        ).first()
        if not existe:
            EntidadService.crear(session, datos)
            creadas += 1

    return {"mensaje": f"{creadas} entidades creadas", "total": len(entidades_ejemplo)}
