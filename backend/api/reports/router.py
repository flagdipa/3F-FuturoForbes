from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select, func
from ...core.database import get_session
from ...models.models import LibroTransacciones, ListaCuentas, Beneficiario, Categoria, Presupuesto
from ...models.models_config import AnioPresupuesto
from ...models.models_plugins import Plugin
from ...core.reports_service import reports_service
from ...core.forecasting_service import forecasting_service
from ...models.models_advanced import TransaccionRecurrente
from datetime import datetime, timedelta, date
from decimal import Decimal

from ..auth.deps import get_current_user

router = APIRouter(prefix="/reportes", tags=["Reportes"], dependencies=[Depends(get_current_user)])

@router.get("/mensual")
def reporte_mensual(
    year: int = Query(datetime.now().year),
    session: Session = Depends(get_session)
):
    """
    Retorna ingresos y gastos agrupados por mes para el año especificado.
    """
    selected_year = year
    
    # Agrupación por mes para ingresos
    ingresos_query = select(
        func.extract('month', LibroTransacciones.fecha_transaccion).label('mes'),
        func.sum(func.abs(LibroTransacciones.monto_transaccion)).label('total')
    ).where(
        func.extract('year', LibroTransacciones.fecha_transaccion) == selected_year,
        LibroTransacciones.codigo_transaccion == 'Deposit'
    ).group_by(func.extract('month', LibroTransacciones.fecha_transaccion))
    
    ingresos = session.exec(ingresos_query).all()
    
    # Agrupación por mes para gastos
    gastos_query = select(
        func.extract('month', LibroTransacciones.fecha_transaccion).label('mes'),
        func.sum(func.abs(LibroTransacciones.monto_transaccion)).label('total')
    ).where(
        func.extract('year', LibroTransacciones.fecha_transaccion) == selected_year,
        LibroTransacciones.codigo_transaccion == 'Withdrawal'
    ).group_by(func.extract('month', LibroTransacciones.fecha_transaccion))
    
    gastos = session.exec(gastos_query).all()
    
    # Estructurar datos: [0..11] para Ene..Dic
    data_ingresos = [0] * 12
    data_gastos = [0] * 12
    
    for mes, total in ingresos:
        if mes: data_ingresos[int(mes)-1] = float(total)
        
    for mes, total in gastos:
        if mes: data_gastos[int(mes)-1] = abs(float(total)) # Gasto positivo para gráfico
        
    return {
        "labels": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
        "ingresos": data_ingresos,
        "gastos": data_gastos
    }

@router.get("/categorias")
def reporte_categorias(
    month: int = Query(None), 
    year: int = Query(None),
    session: Session = Depends(get_session)
):
    """
    Retorna gastos por categoría. Si no se especifican mes/año, busca el último mes con datos.
    """
    if month is None or year is None:
        last_tx = session.exec(select(LibroTransacciones.fecha_transaccion).order_by(LibroTransacciones.fecha_transaccion.desc())).first()
        if last_tx:
            dt = datetime.fromisoformat(last_tx)
            month = dt.month
            year = dt.year
        else:
            now = datetime.now()
            month = now.month
            year = now.year

    query = select(
        Categoria.nombre_categoria,
        func.sum(func.abs(LibroTransacciones.monto_transaccion)).label('total')
    ).join(Categoria, isouter=True)\
     .where(
        func.extract('month', LibroTransacciones.fecha_transaccion) == month,
        func.extract('year', LibroTransacciones.fecha_transaccion) == year,
        LibroTransacciones.codigo_transaccion == 'Withdrawal' # Basado en el código de MMEX
    ).group_by(Categoria.nombre_categoria)\
     .order_by(func.sum(func.abs(LibroTransacciones.monto_transaccion)).desc())
     
    results = session.exec(query).all()
    
    labels = []
    data = []
    
    for cat, total in results:
        labels.append(cat or "Sin Categoría")
        data.append(float(total))
        
    return {
        "labels": labels,
        "data": data
    }

@router.get("/csv")
def descargar_csv(
    start_date: str = Query(None),
    end_date: str = Query(None),
    session: Session = Depends(get_session)
):
    # Filtros base
    query = select(
        LibroTransacciones, 
        ListaCuentas.nombre_cuenta, 
        Beneficiario.nombre_beneficiario, 
        Categoria.nombre_categoria
    ).join(ListaCuentas, isouter=True)\
     .join(Beneficiario, isouter=True)\
     .join(Categoria, isouter=True)

    if start_date:
        query = query.where(LibroTransacciones.fecha_transaccion >= start_date)
    if end_date:
        query = query.where(LibroTransacciones.fecha_transaccion <= end_date)
        
    results = session.exec(query).all()
    
    # Formatear para el servicio
    data = []
    for tx, cuenta, ben, cat in results:
        data.append({
            "fecha_transaccion": tx.fecha_transaccion,
            "cuenta": cuenta,
            "beneficiario": ben,
            "categoria": cat,
            "codigo_transaccion": tx.codigo_transaccion,
            "monto_transaccion": tx.monto_transaccion,
            "notas": tx.notas,
            "estado": tx.estado
        })
        
    buffer = reports_service.generate_csv(data)
    
    filename = f"3F_Reporte_{datetime.now().strftime('%Y%m%d')}.csv"
    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/pdf")
def descargar_pdf(
    start_date: str = Query(None),
    end_date: str = Query(None),
    session: Session = Depends(get_session)
):
    if not start_date:
        start_date = (datetime.now().replace(day=1)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")

    # 1. Obtener Transacciones
    query = select(
        LibroTransacciones, 
        Beneficiario.nombre_beneficiario, 
        Categoria.nombre_categoria
    ).join(Beneficiario, isouter=True)\
     .join(Categoria, isouter=True)\
     .where(LibroTransacciones.fecha_transaccion >= start_date)\
     .where(LibroTransacciones.fecha_transaccion <= end_date)\
     .order_by(LibroTransacciones.fecha_transaccion.desc())
     
    results = session.exec(query).all()
    
    data = []
    total_ingresos = Decimal(0)
    total_gastos = Decimal(0)
    
    for tx, ben, cat in results:
        monto = tx.monto_transaccion
        if tx.codigo_transaccion == 'Deposit':
            total_ingresos += monto
        elif tx.codigo_transaccion == 'Withdrawal':
            total_gastos += abs(monto)
            
        data.append({
            "fecha_transaccion": tx.fecha_transaccion,
            "beneficiario": ben,
            "categoria": cat,
            "monto_transaccion": monto
        })

    buffer = reports_service.generate_pdf(data, start_date, end_date, total_ingresos, total_gastos)
    
    filename = f"3F_Estado_Cuenta_{datetime.now().strftime('%Y%m')}.pdf"
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/tendencia")
def reporte_tendencia(
    meses: int = Query(6),
    session: Session = Depends(get_session)
):
    """
    Calcula la tendencia lineal de los saldos mensuales (Net Worth).
    """
    # 1. Obtener balance neto por mes (simplificado: ingresos - gastos)
    # En un sistema real, esto debería sumar saldos iniciales + flujos
    query = select(
        func.extract('month', LibroTransacciones.fecha_transaccion).label('mes'),
        func.extract('year', LibroTransacciones.fecha_transaccion).label('anio'),
        func.sum(LibroTransacciones.monto_transaccion).label('total')
    ).group_by('anio', 'mes').order_by('anio', 'mes')
    
    results = session.exec(query).all()
    
    points = []
    labels = []
    running_total = 0
    for idx, (mes, anio, total) in enumerate(results):
        running_total += float(total)
        points.append((idx, running_total))
        labels.append(f"{idx}") # Etiquetas simplificadas

    # Verificamos si el plugin de IA está activo
    plugin_ia = session.exec(select(Plugin).where(Plugin.nombre_tecnico == "ia_forecasting")).first()
    ai_enabled = plugin_ia.activo if plugin_ia else False
    
    trend_points = []
    final_labels = labels.copy()

    if ai_enabled:
        regression = forecasting_service.calculate_weighted_regression(points)
        
        # Generar puntos de tendencia (incluyendo proyección futura a 6 meses)
        for i in range(len(points) + 6): 
            val = regression['slope'] * i + regression['intercept']
            trend_points.append(round(val, 2))
        
        final_labels += ["+1", "+2", "+3", "+4", "+5", "+6"]
        
    return {
        "historico": [p[1] for p in points],
        "tendencia": trend_points,
        "labels": final_labels,
        "ai_enabled": ai_enabled
    }

@router.get("/presupuesto-realidad")
def presupuesto_realidad(
    year: int = Query(datetime.now().year),
    month: int = Query(datetime.now().month),
    session: Session = Depends(get_session)
):
    """
    Compara el presupuesto vs la realidad por categoría para un mes específico.
    """
    # 1. Obtener ID del año de presupuesto
    anio_obj = session.exec(select(AnioPresupuesto).where(AnioPresupuesto.anio == year)).first()
    if not anio_obj:
        return {"error": "Configuración de presupuesto no encontrada para el año especificado"}

    # 2. Obtener presupuestos del año
    presupuestos = session.exec(
        select(Presupuesto, Categoria.nombre_categoria)
        .join(Categoria)
        .where(Presupuesto.id_anio_presupuesto == anio_obj.id_anio_presupuesto, Presupuesto.activo == 1)
    ).all()

    # 3. Obtener gastos reales del mes
    gastos_query = select(
        LibroTransacciones.id_categoria,
        func.sum(func.abs(LibroTransacciones.monto_transaccion)).label('total')
    ).where(
        func.extract('year', LibroTransacciones.fecha_transaccion) == year,
        func.extract('month', LibroTransacciones.fecha_transaccion) == month,
        LibroTransacciones.codigo_transaccion == 'Withdrawal'
    ).group_by(LibroTransacciones.id_categoria)

    gastos_reales = {g.id_categoria: float(g.total) for g in session.exec(gastos_query).all()}

    # 4. Consolidar
    comparativa = []
    for pres, cat_nombre in presupuestos:
        # Ajustar monto si es mensual vs anual (asumimos Monthly por ahora según modelo)
        monto_presupuestado = float(pres.monto)
        gasto_real = gastos_reales.get(pres.id_categoria, 0.0)
        
        porcentaje = (gasto_real / monto_presupuestado * 100) if monto_presupuestado > 0 else 0
        
        comparativa.append({
            "categoria": cat_nombre,
            "presupuestado": monto_presupuestado,
            "real": gasto_real,
            "diferencia": monto_presupuestado - gasto_real,
            "porcentaje": round(porcentaje, 2)
        })

    return sorted(comparativa, key=lambda x: x['porcentaje'], reverse=True)
@router.get("/proyeccion-cuenta/{id_cuenta}")
def proyeccion_cuenta(
    id_cuenta: int,
    dias: int = Query(30),
    session: Session = Depends(get_session)
):
    """
    Proyecta el saldo de una cuenta específica usando transacciones programadas.
    """
    cuenta = session.get(ListaCuentas, id_cuenta)
    if not cuenta:
        return {"error": "Cuenta no encontrada"}
        
    # Obtener saldo actual (esto debería calcularse de la tabla transacciones + saldo_inicial)
    total_tx = session.exec(select(func.sum(LibroTransacciones.monto_transaccion)).where(LibroTransacciones.id_cuenta == id_cuenta)).one() or 0
    saldo_actual = float(cuenta.saldo_inicial) + float(total_tx)
    
    # Obtener programadas
    recurring = session.exec(select(TransaccionRecurrente).where(TransaccionRecurrente.id_cuenta == id_cuenta, TransaccionRecurrente.activo == 1)).all()
    recurring_data = [r.dict() for r in recurring]
    
    proyeccion = forecasting_service.forecast_account_balance(Decimal(saldo_actual), recurring_data, dias)
    
    return proyeccion
