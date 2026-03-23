"""
Tags API — v1
Routes: /tags/
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ...models import Tag
from ...dependencies import get_db
from ..auth.deps import get_current_user
from ...models import User

router = APIRouter()


@router.get("/", summary="Listar etiquetas del usuario")
def list_tags(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = select(Tag).where(Tag.user_id == current_user.id).order_by(Tag.name)
    return db.exec(stmt).all()


@router.post("/", summary="Crear etiqueta", status_code=201)
def create_tag(
    name: str,
    color: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tag = Tag(user_id=current_user.id, name=name, color=color)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@router.delete("/{tag_id}", status_code=204)
def delete_tag(
    tag_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tag = db.get(Tag, tag_id)
    if not tag or tag.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Tag not found")
    db.delete(tag)
    db.commit()
    return None
