from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from ...core.database import get_session
from ..auth.deps import get_current_user
from ...models.models import Usuario
from ...models.models_wealth import WealthSnapshot
from ..transactions.router_resumen import obtener_resumen_financiero
from datetime import datetime

from ...core.wealth_service import wealth_service

router = APIRouter(prefix="/wealth", tags=["Wealth Intelligence"])

@router.post("/snapshot")
async def capture_wealth_snapshot(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Captures a current snapshot of the user's wealth.
    """
    return await wealth_service.capture_snapshot(session, current_user.id_usuario)

@router.get("/history")
def get_wealth_history(
    limit: int = 30,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Returns historical snapshots for charting.
    """
    query = select(WealthSnapshot).where(WealthSnapshot.id_usuario == current_user.id_usuario).order_by(WealthSnapshot.fecha.desc()).limit(limit)
    return session.exec(query).all()

@router.get("/history/chart")
def get_wealth_chart_data(
    days: int = 30,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Returns data formatted for Chart.js.
    """
    query = select(WealthSnapshot).where(
        WealthSnapshot.id_usuario == current_user.id_usuario
    ).order_by(WealthSnapshot.fecha.asc()).limit(days)
    
    results = session.exec(query).all()
    
    return {
        "labels": [s.fecha.strftime("%d/%m") for s in results],
        "datasets": [
            {
                "label": "Patrimonio Neto",
                "data": [float(s.patrimonio_neto) for s in results]
            }
        ]
    }

@router.get("/savings-rate")
def get_savings_rate(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Calculates the savings rate for the current month.
    (Income - Expenses) / Income
    """
    resumen = obtener_resumen_financiero(session, current_user.id_usuario)
    ingresos = float(resumen.get("ingresos_mes", 0))
    gastos = float(resumen.get("gastos_mes", 0))
    
    ahorro = ingresos - gastos
    rate = (ahorro / ingresos * 100) if ingresos > 0 else 0
    
    return {
        "ingresos": ingresos,
        "gastos": gastos,
        "ahorro": ahorro,
        "savings_rate_percentage": round(rate, 2),
        "status": "HEALTHY" if rate > 20 else "AVERAGE" if rate > 0 else "CRITICAL"
    }
