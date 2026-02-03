from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ...core.database import get_session
from ...models.models import Presupuesto, Categoria, LibroTransacciones
from sqlalchemy import func
from datetime import datetime
from decimal import Decimal
from typing import List
from .schemas import PresupuestoCrear, PresupuestoLectura

router = APIRouter(prefix="/presupuestos", tags=["Presupuestos"])

@router.get("/", response_model=List[PresupuestoLectura])
def listar_presupuestos(session: Session = Depends(get_session)):
    # 1. Obtener todos los presupuestos activos con nombre de categoría
    query = select(Presupuesto, Categoria.nombre_categoria).join(Categoria, isouter=True).where(Presupuesto.activo == 1)
    results = session.exec(query).all()
    
    # 2. Definir rango de fechas (Mes Actual)
    hoy = datetime.utcnow()
    primer_dia_mes = datetime(hoy.year, hoy.month, 1).isoformat()
    
    lista = []
    for pres, cat_name in results:
        # 3. Calcular gasto real para esta categoría en el mes actual
        # Sumamos transacciones de tipo 'Withdrawal' para la categoría del presupuesto
        gasto_query = select(func.sum(LibroTransacciones.monto_transaccion)).where(
            LibroTransacciones.id_categoria == pres.id_categoria,
            LibroTransacciones.codigo_transaccion == "Withdrawal",
            LibroTransacciones.fecha_transaccion >= primer_dia_mes
        )
        # El resultado puede ser None si no hay transacciones
        gasto_real = session.exec(gasto_query).one() or Decimal("0.00")
        
        # 4. Construir respuesta enriquecida
        data = PresupuestoLectura.from_orm(pres)
        data.nombre_categoria = cat_name
        data.gasto_actual = abs(gasto_real) # Convertir a positivo para visualizar
        
        if pres.monto > 0:
            data.porcentaje = round((float(data.gasto_actual) / float(pres.monto)) * 100, 1)
        else:
            data.porcentaje = 100.0 if data.gasto_actual > 0 else 0.0
            
        lista.append(data)
    
    return lista

@router.post("/", response_model=PresupuestoLectura)
def crear_presupuesto(presupuesto_in: PresupuestoCrear, session: Session = Depends(get_session)):
    nuevo_presupuesto = Presupuesto.from_orm(presupuesto_in)
    session.add(nuevo_presupuesto)
    session.commit()
    session.refresh(nuevo_presupuesto)
    return nuevo_presupuesto

@router.put("/{presupuesto_id}", response_model=PresupuestoLectura)
def actualizar_presupuesto(presupuesto_id: int, presupuesto_in: PresupuestoCrear, session: Session = Depends(get_session)):
    db_presupuesto = session.get(Presupuesto, presupuesto_id)
    if not db_presupuesto:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    
    pres_data = presupuesto_in.dict(exclude_unset=True)
    for key, value in pres_data.items():
        setattr(db_presupuesto, key, value)
    
    session.add(db_presupuesto)
    session.commit()
    session.refresh(db_presupuesto)
    return db_presupuesto
