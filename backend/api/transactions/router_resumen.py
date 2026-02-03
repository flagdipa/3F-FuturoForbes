from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from ...core.database import get_session
from ...models.models import LibroTransacciones, ListaCuentas
from decimal import Decimal
from datetime import datetime

router = APIRouter(prefix="/resumen", tags=["Resumen"])

@router.get("/")
def obtener_resumen_financiero(session: Session = Depends(get_session)):
    """
    Calcula el patrimonio neto, ingresos y gastos del mes actual.
    """
    # 1. Patrimonio Neto (Suma de saldos iniciales + movimientos)
    # Nota: En un sistema completo de partida doble, sumaríamos todos los movimientos.
    # Para el MVP, sumamos saldos de cuentas.
    cuentas = session.exec(select(ListaCuentas)).all()
    patrimonio_neto = sum(c.saldo_inicial for c in cuentas)
    
    # 2. Movimientos del mes actual
    hoy = datetime.utcnow()
    primer_dia_mes = datetime(hoy.year, hoy.month, 1).isoformat()
    
    # Ingresos (Asumiendo que Deposit aumenta el saldo)
    ingresos_query = select(func.sum(LibroTransacciones.monto_transaccion)).where(
        LibroTransacciones.codigo_transaccion == "Deposit",
        LibroTransacciones.fecha_transaccion >= primer_dia_mes
    )
    ingresos = session.exec(ingresos_query).one() or Decimal("0.00")
    
    # Gastos (Asumiendo que Withdrawal disminuye el saldo)
    gastos_query = select(func.sum(LibroTransacciones.monto_transaccion)).where(
        LibroTransacciones.codigo_transaccion == "Withdrawal",
        LibroTransacciones.fecha_transaccion >= primer_dia_mes
    )
    gastos = session.exec(gastos_query).one() or Decimal("0.00")

    return {
        "patrimonio_neto": patrimonio_neto,
        "ingresos_mes": ingresos,
        "gastos_mes": abs(gastos),
        "moneda_base": "ARS",
        "sincronizacion": datetime.utcnow().isoformat()
    }
