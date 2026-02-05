"""
Wealth snapshot models for historical tracking.
Phase 7: Wealth Intelligence HUD
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from decimal import Decimal

class WealthSnapshot(SQLModel, table=True):
    """
    Periodic snapshots of total wealth breakdown.
    Used for historical charts and trend analysis.
    """
    __tablename__ = "wealth_snapshots"
    
    id_snapshot: Optional[int] = Field(default=None, primary_key=True)
    fecha: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    total_liquido: Decimal = Field(default=0, max_digits=20, decimal_places=2)
    total_activos: Decimal = Field(default=0, max_digits=20, decimal_places=2)
    total_inversiones: Decimal = Field(default=0, max_digits=20, decimal_places=2)
    patrimonio_neto: Decimal = Field(default=0, max_digits=20, decimal_places=2)
    
    id_usuario: int = Field(index=True) # Snapshots per user
