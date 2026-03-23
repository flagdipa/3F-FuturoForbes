"""
Themes API — v1
Routes: /themes/
Serves preset theme data. User preference is stored in user.theme_id.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ...dependencies import get_db
from ..auth.deps import get_current_user
from ...models import User
from ...core.themes import get_theme, get_all_themes, THEMES

router = APIRouter()


@router.get("/presets", summary="Listar todos los temas disponibles")
def list_presets():
    return get_all_themes()


@router.get("/presets/{theme_id}", summary="Obtener un tema por ID")
def get_preset(theme_id: str):
    theme = THEMES.get(theme_id)
    if not theme:
        raise HTTPException(status_code=404, detail=f"Theme '{theme_id}' not found")
    return theme


@router.get("/current", summary="Tema activo del usuario")
def get_current_theme(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    theme_id = current_user.theme_id or "dark_neon"
    return get_theme(theme_id)


@router.put("/current", summary="Cambiar tema del usuario")
def set_current_theme(
    body: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    theme_id = body.get("theme_id", "dark_neon")
    if theme_id not in THEMES:
        raise HTTPException(status_code=400, detail=f"Unknown theme '{theme_id}'")
    current_user.theme_id = theme_id
    db.add(current_user)
    db.commit()
    return {"status": "ok", "theme_id": theme_id}
