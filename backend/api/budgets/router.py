from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select
from ...core.database import get_session
from ...models.models import Presupuesto, Categoria, LibroTransacciones, Usuario
from sqlalchemy import func
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from .schemas import PresupuestoCrear, PresupuestoLectura
from ..base_crud import BaseCRUDService
from ..schemas.common import PaginatedResponse
from ..auth.deps import get_current_user

router = APIRouter(prefix="/presupuestos", tags=["Presupuestos"])
budget_service = BaseCRUDService[Presupuesto, PresupuestoCrear, PresupuestoCrear](Presupuesto)

@router.get("/", response_model=PaginatedResponse[PresupuestoLectura])
def listar_presupuestos(
    offset: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """List budgets with real-time spending calculations and pagination"""
    # 1. Obtener todos los presupuestos activos (aprovechando BaseCRUDService logic but extending)
    # Para mantener el cálculo enriquecido, listamos y luego procesamos
    res = budget_service.list(session, offset=offset, limit=limit, filters={"activo": 1})
    
    # 2. Definir rango de fechas (Mes Actual)
    hoy = datetime.utcnow()
    primer_dia_mes = datetime(hoy.year, hoy.month, 1).isoformat()
    
    enriched_data = []
    for pres in res.data:
        # Get category name
        cat = session.get(Categoria, pres.id_categoria)
        cat_name = cat.nombre_categoria if cat else "Sin Categoría"
        
        # 3. Calcular gasto real para esta categoría en el mes actual
        gasto_query = select(func.sum(LibroTransacciones.monto_transaccion)).where(
            LibroTransacciones.id_categoria == pres.id_categoria,
            LibroTransacciones.codigo_transaccion == "Withdrawal",
            LibroTransacciones.fecha_transaccion >= primer_dia_mes
        )
        gasto_real = session.exec(gasto_query).one() or Decimal("0.00")
        
        # 4. Construir respuesta enriquecida
        data = PresupuestoLectura.from_orm(pres)
        data.nombre_categoria = cat_name
        data.gasto_actual = abs(gasto_real)
        
        if pres.monto > 0:
            data.porcentaje = round((float(data.gasto_actual) / float(pres.monto)) * 100, 1)
        else:
            data.porcentaje = 100.0 if data.gasto_actual > 0 else 0.0
            
        enriched_data.append(data)
    
    res.data = enriched_data
    return res

@router.post("/", response_model=PresupuestoLectura)
def crear_presupuesto(
    presupuesto_in: PresupuestoCrear, 
    request: Request,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Create a new budget with audit"""
    return budget_service.create(
        session, presupuesto_in,
        user_id=current_user.id_usuario,
        ip_address=request.client.host
    )

@router.put("/{presupuesto_id}", response_model=PresupuestoLectura)
def actualizar_presupuesto(
    presupuesto_id: int, 
    presupuesto_in: PresupuestoCrear, 
    request: Request,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Update a budget with audit"""
    db_presupuesto = budget_service.get(session, presupuesto_id)
    if not db_presupuesto:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrada")
        
    return budget_service.update(
        session, db_presupuesto, presupuesto_in,
        user_id=current_user.id_usuario,
        ip_address=request.client.host
    )
