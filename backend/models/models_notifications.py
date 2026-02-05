from datetime import datetime
from typing import Optional, Literal
from sqlmodel import SQLModel, Field
from pydantic import BaseModel

class UserNotification(SQLModel, table=True):
    """
    Persistent notification model for history and read tracking.
    """
    __tablename__ = "user_notifications"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="usuarios.id_usuario", index=True)
    
    type: str = Field(index=True) # info, success, warning, error
    title: str
    message: str
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    read: bool = Field(default=False, index=True)
    
    action_url: Optional[str] = None
    action_text: Optional[str] = None

class NotificationRead(BaseModel):
    """Schema for marking a notification as read"""
    read: bool = True
