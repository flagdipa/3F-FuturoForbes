from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from ...core.database import get_session
from ...models.models_config import AnioPresupuesto
from .schemas_advanced import AnioPresupuestoCreate, AnioPresupuestoUpdate, AnioPresupuestoResponse

router = APIRouter(prefix="/years", tags=["Budget Years"])

@router.get("/", response_model=List[AnioPresupuestoResponse])
def list_budget_years(activo: Optional[int] = None, session: Session = Depends(get_session)):
    query = select(AnioPresupuesto)
    if activo is not None:
        query = query.where(AnioPresupuesto.activo == activo)
    query = query.order_by(AnioPresupuesto.anio.desc())
    return session.exec(query).all()

@router.post("/", response_model=AnioPresupuestoResponse, status_code=status.HTTP_201_CREATED)
def create_budget_year(data: AnioPresupuestoCreate, session: Session = Depends(get_session)):
    existing = session.exec(select(AnioPresupuesto).where(AnioPresupuesto.anio == data.anio)).first()
    if existing:
        raise HTTPException(status_code=400, detail="El año ya existe")
    year = AnioPresupuesto(**data.dict())
    session.add(year)
    session.commit()
    session.refresh(year)
    return year

@router.get("/{id_anio}", response_model=AnioPresupuestoResponse)
def get_budget_year(id_anio: int, session: Session = Depends(get_session)):
    year = session.get(AnioPresupuesto, id_anio)
    if not year:
        raise HTTPException(status_code=404, detail="Año no encontrado")
    return year

@router.put("/{id_anio}", response_model=AnioPresupuestoResponse)
def update_budget_year(id_anio: int, data: AnioPresupuestoUpdate, session: Session = Depends(get_session)):
    year = session.get(AnioPresupuesto, id_anio)
    if not year:
        raise HTTPException(status_code=404, detail="Año no encontrado")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(year, key, value)
    session.add(year)
    session.commit()
    session.refresh(year)
    return year
