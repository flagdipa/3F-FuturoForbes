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
