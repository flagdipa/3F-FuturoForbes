from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ...dependencies import get_db
from ...models import Asset, User
from ..auth.deps import get_current_user
from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime

router = APIRouter()

class AssetCreate(BaseModel):
    name: str
    type: str # REAL_ESTATE, VEHICLE, etc.
    currency_code: str
    purchase_price: Optional[Decimal] = None
    notes: Optional[str] = None

class AssetResponse(AssetCreate):
    id: int
    created_at: datetime

@router.get("/", response_model=List[AssetResponse])
def list_assets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    assets = db.exec(select(Asset).where(Asset.deleted_at == None, Asset.user_id == current_user.id)).all()
    return assets

@router.post("/", response_model=AssetResponse)
def create_asset(asset_in: AssetCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    asset = Asset(
        **asset_in.model_dump(),
        user_id=current_user.id
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset
