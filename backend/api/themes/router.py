"""
Theme API Router
Endpoints for theme management and user preferences
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from backend.core.database import get_session
from backend.api.auth.deps import get_current_user
from backend.models.models import Usuario
from backend.core.themes import get_theme, get_all_themes, THEMES
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter(prefix="/themes", tags=["Themes"])


class ThemeResponse(BaseModel):
    """Theme data response"""
    id: str
    name: str
    description: str
    variables: Dict[str, str]


class ThemeListItem(BaseModel):
    """Theme list item"""
    id: str
    name: str
    description: str


class ThemeUpdateRequest(BaseModel):
    """Request to update user theme"""
    theme_id: str


@router.get("/presets", response_model=list[ThemeListItem])
async def list_theme_presets():
    """
    Get list of available theme presets
    """
    return get_all_themes()


@router.get("/presets/{theme_id}", response_model=ThemeResponse)
async def get_theme_preset(theme_id: str):
    """
    Get specific theme preset by ID
    """
    theme = get_theme(theme_id)
    if not theme:
        raise HTTPException(status_code=404, detail=f"Theme '{theme_id}' not found")
    
    return ThemeResponse(
        id=theme["id"],
        name=theme["name"],
        description=theme["description"],
        variables=theme["variables"]
    )


@router.get("/current", response_model=ThemeResponse)
async def get_current_theme(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Get current user's theme preference
    """
    theme_id = current_user.theme_preference or "dark_neon"
    theme = get_theme(theme_id)
    
    return ThemeResponse(
        id=theme["id"],
        name=theme["name"],
        description=theme["description"],
        variables=theme["variables"]
    )


@router.put("/current")
async def update_current_theme(
    data: ThemeUpdateRequest,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Update user's theme preference
    """
    # Validate theme exists
    if data.theme_id not in THEMES:
        raise HTTPException(status_code=400, detail=f"Invalid theme ID: {data.theme_id}")
    
    # Update user preference
    current_user.theme_preference = data.theme_id
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    
    return {
        "message": "Theme updated successfully",
        "theme_id": data.theme_id
    }
