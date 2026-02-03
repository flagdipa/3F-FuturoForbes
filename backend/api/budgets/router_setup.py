"""
Budget Setup Router (Phase 3)
Handles years and administrative settings for budgets.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from ...core.database import get_session
from ...models.models_config import AñoPresupuesto
from .schemas_advanced import AñoPresupuestoCreate, AñoPresupuestoUpdate, AñoPresupuestoResponse

router = APIRouter(prefix="/setup", tags=["Budget Setup"])

@router.get("/years", response_model=List[AñoPresupuestoResponse])
def list_budget_years(
    activo: Optional[int] = None,
    session: Session = Depends(get_session)
):
    """List all configured budget years"""
    query = select(AñoPresupuesto)
    if activo is not None:
        query = query.where(AñoPresupuesto.activo == activo)
    query = query.order_by(AñoPresupuesto.anio.desc())
    
    return session.exec(query).all()

@router.post("/years", response_model=AñoPresupuestoResponse, status_code=status.HTTP_201_CREATED)
def create_budget_year(data: AñoPresupuestoCreate, session: Session = Depends(get_session)):
    """Create a new year for budgeting"""
    # Check if year already exists
    existing = session.exec(select(AñoPresupuesto).where(AñoPresupuesto.anio == data.anio)).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"El año {data.anio} ya está configurado")
        
    year = AñoPresupuesto(**data.dict())
    session.add(year)
    session.commit()
    session.refresh(year)
    return year

@router.get("/years/{id_año}", response_model=AñoPresupuestoResponse)
def get_budget_year(id_año: int, session: Session = Depends(get_session)):
    """Get specific budget year details"""
    year = session.get(AñoPresupuesto, id_año)
    if not year:
        raise HTTPException(status_code=404, detail="Año de presupuesto no encontrado")
    return year

@router.put("/years/{id_año}", response_model=AñoPresupuestoResponse)
def update_budget_year(
    id_año: int, 
    data: AñoPresupuestoUpdate, 
    session: Session = Depends(get_session)
):
    """Update settings for a budget year"""
    year = session.get(AñoPresupuesto, id_año)
    if not year:
        raise HTTPException(status_code=404, detail="Año de presupuesto no encontrado")
        
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(year, key, value)
        
    session.add(year)
    session.commit()
    session.refresh(year)
    return year

@router.delete("/years/{id_año}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget_year(id_año: int, session: Session = Depends(get_session)):
    """Delete a budget year configuration"""
    year = session.get(AñoPresupuesto, id_año)
    if not year:
        raise HTTPException(status_code=404, detail="Año de presupuesto no encontrado")
    
    session.delete(year)
    session.commit()
    return None
