from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select, func
from ...core.database import get_session
from ...models.models import LibroTransacciones, ListaCuentas, Beneficiario, Categoria, Presupuesto, Usuario
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
    # Expresiones para extraer mes y año (más compatibles con SQLModel/SQLAlchemy)
    expr_mes = func.extract('month', LibroTransacciones.fecha_transaccion)
    expr_anio = func.extract('year', LibroTransacciones.fecha_transaccion)

    # 1. Obtener balance neto por mes (ingresos + gastos)
    query = select(
        expr_mes.label('mes'),
        expr_anio.label('anio'),
        func.sum(LibroTransacciones.monto_transaccion).label('total')
    ).group_by(expr_anio, expr_mes).order_by(expr_anio, expr_mes)
    
    try:
        results = session.exec(query).all()
    except Exception as e:
        # Fallback si func.extract falla (ej: SQLite string format)
        results = []

    points = []
    labels = []
    running_total = 0
    
    if results:
        for idx, row in enumerate(results):
            # Acceso por índice o atributo según el driver
            mes, anio, total = row
            val_total = float(total or 0)
            running_total += val_total
            points.append((idx, running_total))
            labels.append(f"{idx}")
    else:
        # Si no hay datos, inicializamos un punto en cero
        points = [(0, 0.0)]
        labels = ["0"]

    # Verificamos si el plugin de IA está activo
    ai_enabled = False
    try:
        plugin_ia = session.exec(select(Plugin).where(Plugin.nombre_tecnico == "ia_forecasting")).first()
        ai_enabled = plugin_ia.activo if plugin_ia else False
    except:
        pass
    
    trend_points = []
    final_labels = labels.copy()

    if ai_enabled and len(points) >= 1:
        regression = forecasting_service.calculate_weighted_regression(points)
        
        # Generar puntos de tendencia (incluyendo proyección futura a 6 meses)
        for i in range(len(points) + 6): 
            val = regression['slope'] * i + regression['intercept']
            trend_points.append(round(val, 2))
        
        final_labels += ["+1", "+2", "+3", "+4", "+5", "+6"]
    else:
        # Tendencia plana si no hay IA o datos suficientes
        trend_points = [p[1] for p in points]
        
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
@router.get("/cashflow")
def reporte_cashflow(
    year: int = Query(datetime.now().year),
    session: Session = Depends(get_session)
):
    """
    Retorna Ingresos Reales, Gastos Reales y Presupuesto Mensual Agregado por mes.
    """
    # 1. Obtener Presupuesto Mensual Total del año (Asumimos Monthly por simplicidad)
    # Sumamos todos los presupuestos activos del año 2026 por categoría
    budget_query = select(
        func.sum(Presupuesto.monto).label('total')
    ).join(AnioPresupuesto)\
     .where(AnioPresupuesto.anio == year, Presupuesto.activo == 1)
    
    total_budget_monthly = session.exec(budget_query).one() or 0
    total_budget_monthly = float(total_budget_monthly)

    # 2. Obtener Ingresos Reales por mes
    ingresos_query = select(
        func.extract('month', LibroTransacciones.fecha_transaccion).label('mes'),
        func.sum(func.abs(LibroTransacciones.monto_transaccion)).label('total')
    ).where(
        func.extract('year', LibroTransacciones.fecha_transaccion) == year,
        LibroTransacciones.codigo_transaccion == 'Deposit'
    ).group_by(func.extract('month', LibroTransacciones.fecha_transaccion))
    
    ingresos_mes = {int(mes): float(total) for mes, total in session.exec(ingresos_query).all() if mes}
    
    # 3. Obtener Gastos Reales por mes
    gastos_query = select(
        func.extract('month', LibroTransacciones.fecha_transaccion).label('mes'),
        func.sum(func.abs(LibroTransacciones.monto_transaccion)).label('total')
    ).where(
        func.extract('year', LibroTransacciones.fecha_transaccion) == year,
        LibroTransacciones.codigo_transaccion == 'Withdrawal'
    ).group_by(func.extract('month', LibroTransacciones.fecha_transaccion))
    
    gastos_mes = {int(mes): float(total) for mes, total in session.exec(gastos_query).all() if mes}

    # 4. Consolidar datos
    labels = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    actual_income = []
    actual_expense = []
    budget_expense = []
    variances = []

    for i in range(1, 13):
        inc = ingresos_mes.get(i, 0.0)
        exp = gastos_mes.get(i, 0.0)
        actual_income.append(inc)
        actual_expense.append(exp)
        budget_expense.append(total_budget_monthly)
        
        # Desviación (Presupuesto - Real) -> Positivo es bueno (menos gasto), Negativo es malo (exceso)
        variance = total_budget_monthly - exp
        variances.append(variance)

    return {
        "labels": labels,
        "datasets": [
            {"label": "Ingresos Reales", "data": actual_income, "type": "bar"},
            {"label": "Gastos Reales", "data": actual_expense, "type": "bar"},
            {"label": "Presupuesto (Gastos)", "data": budget_expense, "type": "line"}
        ],
        "summary": {
            "total_actual_income": sum(actual_income),
            "total_actual_expense": sum(actual_expense),
            "total_budget": total_budget_monthly * 12,
            "monthly_budget": total_budget_monthly
        },
        "variances": variances
    }

@router.get("/heatmap")
def reporte_heatmap(
    month: int = Query(None),
    year: int = Query(None),
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Agrupa gastos por día de la semana y hora para visualización de frecuencia.
    """
    from sqlalchemy import text
    
    where_clause = "WHERE codigo_transaccion = 'Withdrawal'"
    params = {}
    
    if month:
        where_clause += " AND MONTH(fecha_transaccion) = :month"
        params["month"] = month
    if year:
        where_clause += " AND YEAR(fecha_transaccion) = :year"
        params["year"] = year
        
    # Query nativo para MySQL: DAYOFWEEK (1=Dom, 7=Sab), HOUR
    query = text(f"""
        SELECT 
            DAYOFWEEK(fecha_transaccion) as dia_semana,
            HOUR(fecha_transaccion) as hora,
            COUNT(*) as frecuencia,
            SUM(ABS(monto_transaccion)) as volumen
        FROM libro_transacciones
        {where_clause}
        GROUP BY dia_semana, hora
        ORDER BY dia_semana, hora
    """)
    
    results = session.execute(query, params).all()
    
    return [
        {
            "day": r.dia_semana, 
            "hour": r.hora, 
            "count": r.frecuencia, 
            "value": float(r.volumen)
        } 
        for r in results
    ]

