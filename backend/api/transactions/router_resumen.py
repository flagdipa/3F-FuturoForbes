from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, func
from ...core.database import get_session
from ...models.models import LibroTransacciones, ListaCuentas, Usuario, Presupuesto
from ...models.models_config import AnioPresupuesto, Configuracion
from ..auth.deps import get_current_user
from decimal import Decimal
from datetime import datetime

from ...core.wealth_service import wealth_service
from ...core.fx_service import fx_service

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

    # --- Presupuesto del Mes ---
    current_year = hoy.year
    budget_query = select(func.sum(Presupuesto.monto)).join(AnioPresupuesto)\
        .where(AnioPresupuesto.anio == current_year, Presupuesto.activo == 1)
    
    presupuesto_mensual = session.exec(budget_query).one() or Decimal("0.00")
    presupuesto_revalued = fx_service.convert(presupuesto_mensual, "ARS", currency, wealth["rates"])

    # Conversión de flujos del mes
    ingresos_revalued = fx_service.convert(ingresos, "ARS", currency, wealth["rates"])
    gastos_revalued = fx_service.convert(gastos, "ARS", currency, wealth["rates"])


    # --- Proyección de Cierre de Mes ---
    import calendar
    ultimo_dia = calendar.monthrange(hoy.year, hoy.month)[1]
    dias_transcurridos = hoy.day
    dias_restantes = ultimo_dia - dias_transcurridos
    
    # Burn rate diario (basado en gastos del mes)
    burn_rate_diario = abs(float(gastos_revalued)) / dias_transcurridos if dias_transcurridos > 0 else 0
    gasto_proyectado_restante = burn_rate_diario * dias_restantes
    
    # Estimación de cierre: Patrimonio actual - Gasto proyectado (simplificado)
    # También podemos proyectar ingresos si hay un histórico, pero por ahora burn-rate de gastos es más prudente.
    proyeccion_cierre = float(wealth["patrimonio_neto"]) - gasto_proyectado_restante

    return {
        "patrimonio_neto": float(wealth["patrimonio_neto"]),
        "total_liquido": float(wealth["total_liquido"]),
        "total_activos": float(wealth["total_activos"]),
        "total_inversiones": float(wealth["total_inversiones"]),
        "ingresos_mes": float(ingresos_revalued),
        "gastos_mes": abs(float(gastos_revalued)),
        "presupuesto_mes": float(presupuesto_revalued),
        "proyeccion_cierre": round(proyeccion_cierre, 2),
        "dias_restantes": dias_restantes,
        "burn_rate_diario": round(burn_rate_diario, 2),
        "moneda_base": currency,
        "sincronizacion": datetime.utcnow().isoformat()
    }

