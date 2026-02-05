from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, func
from ...core.database import get_session
from ...models.models import LibroTransacciones, ListaCuentas, Usuario
from ...models.models_advanced import Activo, Inversion
from ..auth.deps import get_current_user
from decimal import Decimal
from datetime import datetime

from ...core.wealth_service import wealth_service

router = APIRouter(prefix="/resumen", tags=["Resumen"])

@router.get("/")
async def obtener_resumen_financiero(
    currency: str = Query("ARS"),
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Calcula el patrimonio neto integral y flujos del mes.
    """
    wealth = await wealth_service.calculate_total_wealth(session, current_user.id_usuario, currency)
    
    # Movimientos del mes actual (Flujo de Caja siempre en ARS para consistencia de registros)
    # pero podríamos convertirlo opcionalmente en el futuro.
    hoy = datetime.utcnow()
    primer_dia_mes = datetime(hoy.year, hoy.month, 1).isoformat()
    
    ingresos = session.exec(select(func.sum(LibroTransacciones.monto_transaccion)).where(
        LibroTransacciones.codigo_transaccion == "Deposit",
        LibroTransacciones.fecha_transaccion >= primer_dia_mes
    )).one() or Decimal("0.00")
    
    gastos = session.exec(select(func.sum(LibroTransacciones.monto_transaccion)).where(
        LibroTransacciones.codigo_transaccion == "Withdrawal",
        LibroTransacciones.fecha_transaccion >= primer_dia_mes
    )).one() or Decimal("0.00")

    # Convertir ingresos/gastos a la moneda objetivo para el HUD
    ingresos_revalued = fx_service.convert(ingresos, "ARS", currency, wealth["rates"])
    gastos_revalued = fx_service.convert(gastos, "ARS", currency, wealth["rates"])

    return {
        "patrimonio_neto": float(wealth["patrimonio_neto"]),
        "total_liquido": float(wealth["total_liquido"]),
        "total_activos": float(wealth["total_activos"]),
        "total_inversiones": float(wealth["total_inversiones"]),
        "ingresos_mes": float(ingresos_revalued),
        "gastos_mes": abs(float(gastos_revalued)),
        "moneda_base": currency,
        "sincronizacion": datetime.utcnow().isoformat()
    }
