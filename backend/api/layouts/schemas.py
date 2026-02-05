"""
Layout API Schemas
Request/Response models for layout persistence
"""
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime


class LayoutSave(BaseModel):
    """Schema for saving a layout"""
    layout_config: List[Dict[str, Any]]  # GridStack widget positions
    
    class Config:
        json_schema_extra = {
            "example": {
                "layout_config": [
                    {"id": "widget-1", "x": 0, "y": 0, "w": 4, "h": 3},
                    {"id": "widget-2", "x": 4, "y": 0, "w": 4, "h": 3}
                ]
            }
        }


class LayoutResponse(BaseModel):
    """Schema for layout response"""
    page_name: str
    layout_config: List[Dict[str, Any]]
    updated_at: datetime
    
    class Config:
        from_attributes = True
