"""
Notification System - Backend
Server-Sent Events (SSE) for real-time notifications
"""
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select, desc
from backend.core.database import get_session
from backend.api.auth.deps import get_current_user
from backend.models.models import Usuario
from backend.models.models_notifications import UserNotification, NotificationRead
from pydantic import BaseModel, Field
from typing import Optional, Literal, List
from datetime import datetime
import asyncio
import json
import uuid

router = APIRouter(prefix="/notifications", tags=["Notifications"])

# In-memory notification queue per user (for SSE delivery)
user_notification_queues = {}



class NotificationSchema(BaseModel):
    """Notification schema for SSE and API"""
    id: str
    id_db: Optional[int] = None
    type: Literal["info", "success", "warning", "error"]
    title: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    read: bool = False
    action_url: Optional[str] = None
    action_text: Optional[str] = None


async def notification_generator(user_id: int):
    """
    SSE generator for user notifications
    Yields notifications as they arrive
    """
    # Create queue for this user if it doesn't exist
    if user_id not in user_notification_queues:
        user_notification_queues[user_id] = asyncio.Queue()
    
    queue = user_notification_queues[user_id]
    
    try:
        # Send initial connection message
        yield f"data: {json.dumps({'type': 'connected', 'message': 'Notification stream connected'})}\n\n"
        
        # Keep connection alive and send notifications
        while True:
            try:
                # Wait for notification with timeout for keep-alive
                notification = await asyncio.wait_for(queue.get(), timeout=30.0)
                
                # Send notification
                yield f"data: {json.dumps(notification.dict())}\n\n"
                
            except asyncio.TimeoutError:
                # Send keep-alive ping every 30 seconds
                yield f": keep-alive\n\n"
                
    except asyncio.CancelledError:
        # Client disconnected
        pass
    finally:
        # Cleanup queue when connection closes
        if user_id in user_notification_queues:
            del user_notification_queues[user_id]


@router.get("/stream")
async def notification_stream(
    request: Request,
    current_user: Usuario = Depends(get_current_user)
):
    """
    SSE endpoint for real-time notifications
    Client connects here to receive push notifications
    """
    return StreamingResponse(
        notification_generator(current_user.id_usuario),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive"
        }
    )


@router.get("/", response_model=List[UserNotification])
async def get_notifications(
    limit: int = 20,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Get user notification history"""
    statement = select(UserNotification).where(
        UserNotification.user_id == current_user.id_usuario
    ).order_by(desc(UserNotification.timestamp)).limit(limit)
    
    results = session.exec(statement).all()
    return results


@router.put("/{id}/read", response_model=UserNotification)
async def mark_as_read(
    id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Mark a notification as read"""
    notification = session.get(UserNotification, id)
    if not notification or notification.user_id != current_user.id_usuario:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.read = True
    session.add(notification)
    session.commit()
    session.refresh(notification)
    return notification


@router.put("/read-all")
async def mark_all_as_read(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Mark all notifications for the user as read"""
    statement = select(UserNotification).where(
        UserNotification.user_id == current_user.id_usuario,
        UserNotification.read == False
    )
    notifications = session.exec(statement).all()
    for n in notifications:
        n.read = True
        session.add(n)
    session.commit()
    return {"message": "All notifications marked as read"}

async def clear_notifications(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Clear all user notifications"""
    statement = select(UserNotification).where(UserNotification.user_id == current_user.id_usuario)
    notifications = session.exec(statement).all()
    for n in notifications:
        session.delete(n)
    session.commit()
    return {"message": "Notifications cleared"}


async def send_notification(user_id: int, notification_data: NotificationSchema, session: Optional[Session] = None):
    """
    Send a notification to a specific user.
    Saves to DB and pushes to SSE if user is connected.
    """
    # 1. Save to DB if session provided or get new session
    if not session:
        from backend.core.database import SessionLocal
        with SessionLocal() as db_session:
            db_notif = UserNotification(
                user_id=user_id,
                type=notification_data.type,
                title=notification_data.title,
                message=notification_data.message,
                action_url=notification_data.action_url,
                action_text=notification_data.action_text,
                timestamp=notification_data.timestamp
            )
            db_session.add(db_notif)
            db_session.commit()
            db_session.refresh(db_notif)
            notification_data.id_db = db_notif.id
    else:
        db_notif = UserNotification(
            user_id=user_id,
            type=notification_data.type,
            title=notification_data.title,
            message=notification_data.message,
            action_url=notification_data.action_url,
            action_text=notification_data.action_text,
            timestamp=notification_data.timestamp
        )
        session.add(db_notif)
        session.commit()
        session.refresh(db_notif)
        notification_data.id_db = db_notif.id

    # 2. Push to SSE queue if user is online
    if user_id in user_notification_queues:
        await user_notification_queues[user_id].put(notification_data)
        return True
    return False


# Helper functions for common notification types
async def notify_success(user_id: int, title: str, message: str, action_url: Optional[str] = None, action_text: Optional[str] = None):
    """Send success notification"""
    notif = NotificationSchema(
        id=str(uuid.uuid4()),
        type="success",
        title=title,
        message=message,
        action_url=action_url,
        action_text=action_text
    )
    await send_notification(user_id, notif)


async def notify_error(user_id: int, title: str, message: str):
    """Send error notification"""
    notif = NotificationSchema(
        id=str(uuid.uuid4()),
        type="error",
        title=title,
        message=message
    )
    await send_notification(user_id, notif)


async def notify_info(user_id: int, title: str, message: str, action_url: Optional[str] = None, action_text: Optional[str] = None):
    """Send info notification"""
    notif = NotificationSchema(
        id=str(uuid.uuid4()),
        type="info",
        title=title,
        message=message,
        action_url=action_url,
        action_text=action_text
    )
    await send_notification(user_id, notif)


async def notify_warning(user_id: int, title: str, message: str):
    """Send warning notification"""
    notif = NotificationSchema(
        id=str(uuid.uuid4()),
        type="warning",
        title=title,
        message=message
    )
    await send_notification(user_id, notif)


# Export notification helpers
__all__ = [
    "router",
    "send_notification",
    "notify_success",
    "notify_error",
    "notify_info",
    "notify_warning",
    "NotificationSchema"
]

