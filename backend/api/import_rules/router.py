from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from ...core.database import get_session
from ..auth.deps import get_current_user
from ...models.models import Usuario
from ...models.models_extended import ReglaImportacion
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/import-rules", tags=["Reglas de Importación"])

# --- Schemas ---

class ImportRuleCreate(BaseModel):
    patron: str
    id_categoria: Optional[int] = None
    id_beneficiario: Optional[int] = None
    prioridad: int = 0

class ImportRuleUpdate(BaseModel):
    patron: Optional[str] = None
    id_categoria: Optional[int] = None
    id_beneficiario: Optional[int] = None
    prioridad: Optional[int] = None
    activo: Optional[int] = None


# --- Endpoints ---

@router.get("/", response_model=List[ReglaImportacion])
def list_import_rules(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """List all import rules for the current user, ordered by priority desc."""
    statement = (
        select(ReglaImportacion)
        .where(ReglaImportacion.id_usuario == current_user.id_usuario)
        .order_by(ReglaImportacion.prioridad.desc())
    )
    return session.exec(statement).all()

@router.post("/", response_model=ReglaImportacion)
def create_import_rule(
    rule_in: ImportRuleCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Create a new import rule for auto-categorizing bank CSV imports."""
    if not rule_in.patron or not rule_in.patron.strip():
        raise HTTPException(status_code=400, detail="El patrón no puede estar vacío")

    rule = ReglaImportacion(
        id_usuario=current_user.id_usuario,
        patron=rule_in.patron.strip(),
        id_categoria=rule_in.id_categoria,
        id_beneficiario=rule_in.id_beneficiario,
        prioridad=rule_in.prioridad
    )
    session.add(rule)
    session.commit()
    session.refresh(rule)
    return rule

@router.put("/{rule_id}", response_model=ReglaImportacion)
def update_import_rule(
    rule_id: int,
    rule_in: ImportRuleUpdate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Update an existing import rule."""
    db_rule = session.get(ReglaImportacion, rule_id)
    if not db_rule or db_rule.id_usuario != current_user.id_usuario:
        raise HTTPException(status_code=404, detail="Regla no encontrada")

    update_data = rule_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_rule, key, value)

    session.add(db_rule)
    session.commit()
    session.refresh(db_rule)
    return db_rule

@router.delete("/{rule_id}")
def delete_import_rule(
    rule_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Delete an import rule."""
    db_rule = session.get(ReglaImportacion, rule_id)
    if not db_rule or db_rule.id_usuario != current_user.id_usuario:
        raise HTTPException(status_code=404, detail="Regla no encontrada")

    session.delete(db_rule)
    session.commit()
    return {"ok": True}
