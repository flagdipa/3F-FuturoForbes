"""
Layout Management Router
API endpoints for saving and loading user-specific GridStack layouts
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from backend.core.database import get_session
from backend.models.models_layouts import UserLayout
from backend.api.auth.deps import get_current_user
from backend.models.models import Usuario  # Changed from User
from .schemas import LayoutSave, LayoutResponse
import json
from datetime import datetime

router = APIRouter(prefix="/layouts", tags=["Layouts"])


@router.get("/{page_name}", response_model=LayoutResponse)
async def get_layout(
    page_name: str,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Get saved layout for a specific page
    """
    layout = session.exec(
        select(UserLayout)
        .where(UserLayout.user_id == current_user.id_usuario)
        .where(UserLayout.page_name == page_name)
    ).first()
    
    if not layout:
        raise HTTPException(
            status_code=404,
            detail=f"No custom layout found for page '{page_name}'"
        )
    
    return LayoutResponse(
        page_name=layout.page_name,
        layout_config=json.loads(layout.layout_config),
        updated_at=layout.updated_at
    )


@router.post("/{page_name}", response_model=LayoutResponse)
async def save_layout(
    page_name: str,
    data: LayoutSave,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Save or update layout configuration for a page
    """
    # Check if layout exists
    existing = session.exec(
        select(UserLayout)
        .where(UserLayout.user_id == current_user.id_usuario)
        .where(UserLayout.page_name == page_name)
    ).first()
    
    layout_json = json.dumps(data.layout_config)
    
    if existing:
        # Update existing layout
        existing.layout_config = layout_json
        existing.updated_at = datetime.utcnow()
        session.add(existing)
    else:
        # Create new layout
        layout = UserLayout(
            user_id=current_user.id_usuario,
            page_name=page_name,
            layout_config=layout_json
        )
        session.add(layout)
    
    session.commit()
    
    # Refresh to get the updated object
    if existing:
        session.refresh(existing)
        result = existing
    else:
        session.refresh(layout)
        result = layout
    
    return LayoutResponse(
        page_name=result.page_name,
        layout_config=json.loads(result.layout_config),
        updated_at=result.updated_at
    )


@router.delete("/{page_name}", status_code=status.HTTP_204_NO_CONTENT)
async def reset_layout(
    page_name: str,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Delete saved layout (reset to default)
    """
    layout = session.exec(
        select(UserLayout)
        .where(UserLayout.user_id == current_user.id_usuario)
        .where(UserLayout.page_name == page_name)
    ).first()
    
    if layout:
        session.delete(layout)
        session.commit()
    
    return None
