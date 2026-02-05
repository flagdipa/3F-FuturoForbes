"""
Layout Management Models
Stores user-specific GridStack widget positions for personalized dashboards
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class UserLayout(SQLModel, table=True):
    """
    Store GridStack layout configurations per user and page
    """
    __tablename__ = "user_layouts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="usuarios.id_usuario", index=True)
    page_name: str = Field(index=True)  # "dashboard", "settings", "assets", etc.
    layout_config: str  # JSON string of GridStack positions
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "page_name": "dashboard",
                "layout_config": '[{"id":"widget-1","x":0,"y":0,"w":4,"h":3}]'
            }
        }
