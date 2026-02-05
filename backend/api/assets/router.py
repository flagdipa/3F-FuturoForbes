"""
API Router for Assets (Activos)
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select
from typing import List, Optional
from backend.core.database import get_session
from backend.models.models_advanced import Activo, HistorialActivo
from .schemas import (
    ActivoCreate, ActivoUpdate, ActivoResponse,
    HistorialActivoCreate, HistorialActivoResponse
)

router = APIRouter(prefix="/assets", tags=["Assets"])

# ==================== ASSETS CRUD ====================

@router.get("/", response_model=List[ActivoResponse])
def list_assets(
    activo: Optional[int] = None,
    session: Session = Depends(get_session)
):
    """List all assets"""
    query = select(Activo)
    if activo is not None:
        query = query.where(Activo.activo == activo)
    
    results = session.exec(query).all()
    return results

@router.post("/", response_model=ActivoResponse, status_code=status.HTTP_201_CREATED)
def create_asset(data: ActivoCreate, session: Session = Depends(get_session)):
    """Create a new physical asset"""
    asset = Activo(**data.dict())
    session.add(asset)
    session.commit()
    session.refresh(asset)
    
    # Create initial history entry
    history = HistorialActivo(
        id_activo=asset.id_activo,
        fecha=asset.fecha_compra or date.today() if hasattr(asset, 'fecha_compra') else date.today(),
        valor=asset.valor_inicial,
        notas="Valor inicial al crear activo"
    )
    session.add(history)
    session.commit()
    
    return asset

from datetime import date

@router.get("/{id_activo}", response_model=ActivoResponse)
def get_asset(id_activo: int, session: Session = Depends(get_session)):
    """Get specific asset details"""
    asset = session.get(Activo, id_activo)
    if not asset:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    return asset

@router.put("/{id_activo}", response_model=ActivoResponse)
def update_asset(
    id_activo: int,
    data: ActivoUpdate,
    session: Session = Depends(get_session)
):
    """Update asset metadata or current value"""
    asset = session.get(Activo, id_activo)
    if not asset:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    
    # If value is updated, add to history
    if data.valor_actual is not None and data.valor_actual != asset.valor_actual:
        history = HistorialActivo(
            id_activo=asset.id_activo,
            fecha=date.today(),
            valor=data.valor_actual,
            notas="Actualización manual de valor"
        )
        session.add(history)
    
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(asset, key, value)
    
    session.add(asset)
    session.commit()
    session.refresh(asset)
    
    # Notify about manual value change
    if data.valor_actual is not None:
        from ..notifications.router import notify_info
        import asyncio
        asyncio.create_task(notify_info(
            user_id=1, # Default user for now
            title="Activo Actualizado",
            message=f"El valor de '{asset.nombre_activo}' ha sido actualizado a {asset.valor_actual}."
        ))
        
    return asset

@router.delete("/{id_activo}")
def delete_asset(id_activo: int, session: Session = Depends(get_session)):
    """Delete asset and its history"""
    asset = session.get(Activo, id_activo)
    if not asset:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    
    asset_name = asset.nombre_activo
    session.delete(asset)
    session.commit()
    
    # Notify about deletion
    from ..notifications.router import notify_warning
    import asyncio
    asyncio.create_task(notify_warning(
        user_id=1, # Default user for now
        title="Activo Eliminado",
        message=f"Se ha eliminado el activo '{asset_name}'."
    ))
    
    return {"message": "Activo eliminado"}

# ==================== ASSET HISTORY ====================

@router.get("/{id_activo}/history", response_model=List[HistorialActivoResponse])
def get_asset_history(id_activo: int, session: Session = Depends(get_session)):
    """Get value history for an asset"""
    # Verify asset exists
    asset = session.get(Activo, id_activo)
    if not asset:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
        
    query = select(HistorialActivo).where(HistorialActivo.id_activo == id_activo).order_by(HistorialActivo.fecha.desc())
    results = session.exec(query).all()
    return results

@router.post("/history", response_model=HistorialActivoResponse, status_code=status.HTTP_201_CREATED)
def add_history_entry(data: HistorialActivoCreate, session: Session = Depends(get_session)):
    """Add a manual value entry to asset history"""
    # Verify asset exists
    asset = session.get(Activo, data.id_activo)
    if not asset:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
        
    history = HistorialActivo(**data.dict())
    session.add(history)
    
    # Update current value in asset
    asset.valor_actual = data.valor
    session.add(asset)
    
    session.commit()
    session.refresh(history)
    return history
