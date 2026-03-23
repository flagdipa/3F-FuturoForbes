import os
import shutil
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session, select
from pydantic import BaseModel

from ...dependencies import get_db
from ...models.models_v2 import Attachment, Directory, Account, Payee, User
from ..auth.deps import get_current_user

router = APIRouter()

# ─── Configuración ───────────────────────────────────────────────────────────
VAULT_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "attachments")


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def _build_generated_name(original: str, origin_code: str, dest_code: str) -> str:
    """
    Genera el nombre estándar:
    YYMMDD_hhmm_<origen>_<destino_o_benef>.<ext>
    """
    now = datetime.now()
    timestamp = now.strftime("%y%m%d_%H%M")
    ext = os.path.splitext(original)[1].lower()  # mantiene la extensión original
    return f"{timestamp}_{origin_code}_{dest_code}{ext}"


# ─── Schemas ─────────────────────────────────────────────────────────────────
class DirectoryCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None

class DirectoryResponse(BaseModel):
    id: int
    name: str
    path: str
    parent_id: Optional[int]

class AttachmentResponse(BaseModel):
    id: int
    original_filename: str
    generated_filename: str
    file_path: str
    entity_type: Optional[str]
    entity_id: Optional[int]
    directory_id: Optional[int]
    mime_type: Optional[str]
    created_at: datetime


# ─── Endpoints de Directorios ─────────────────────────────────────────────────
@router.get("/directories", response_model=List[DirectoryResponse])
def list_directories(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dirs = db.exec(select(Directory).where(Directory.user_id == current_user.id, Directory.deleted_at == None)).all()
    return dirs


@router.post("/directories", response_model=DirectoryResponse)
def create_directory(data: DirectoryCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    parent_path = ""
    if data.parent_id:
        parent = db.get(Directory, data.parent_id)
        if not parent or parent.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Carpeta padre no encontrada")
        parent_path = parent.path

    full_path = f"{parent_path}/{data.name}".lstrip("/")
    directory = Directory(
        user_id=current_user.id,
        name=data.name,
        parent_id=data.parent_id,
        path=full_path
    )
    db.add(directory)
    db.commit()
    db.refresh(directory)

    # Crea la carpeta física en disco
    physical = os.path.join(VAULT_ROOT, str(current_user.id), full_path)
    _ensure_dir(physical)
    return directory


# ─── Endpoints de Archivos ────────────────────────────────────────────────────
@router.get("/", response_model=List[AttachmentResponse])
def list_attachments(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.exec(select(Attachment).where(Attachment.user_id == current_user.id, Attachment.deleted_at == None)).all()


@router.post("/upload", response_model=AttachmentResponse)
async def upload_file(
    file: UploadFile = File(...),
    entity_type: Optional[str] = Form(None),
    entity_id: Optional[int] = Form(None),
    directory_id: Optional[int] = Form(None),
    origin_account_id: Optional[int] = Form(None),
    dest_account_id: Optional[int] = Form(None),
    payee_id: Optional[int] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sube un archivo a la Bóveda.
    Auto-renombra bajo el formato YYMMDD_hhmm_<origen>_<destino_o_benef>.<ext>
    usando el campo `code` de la Account o Payee correspondiente.
    """
    # Determinar los códigos para el nombre
    origin_code = "SIN-ORIGEN"
    dest_code   = "SIN-DESTINO"

    if origin_account_id:
        acc = db.get(Account, origin_account_id)
        if acc and acc.user_id == current_user.id:
            origin_code = acc.code or f"ACC{acc.id}"

    if dest_account_id:
        dest = db.get(Account, dest_account_id)
        if dest and dest.user_id == current_user.id:
            dest_code = dest.code or f"ACC{dest.id}"
    elif payee_id:
        payee = db.get(Payee, payee_id)
        if payee and payee.user_id == current_user.id:
            dest_code = payee.code or f"PAY{payee.id}"

    # Generar nombre estandarizado
    original_name   = file.filename or "archivo"
    generated_name  = _build_generated_name(original_name, origin_code, dest_code)

    # Determinar directorio físico de destino
    sub_path = ""
    if directory_id:
        directory = db.get(Directory, directory_id)
        if not directory or directory.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Carpeta no encontrada")
        sub_path = directory.path

    physical_dir = os.path.join(VAULT_ROOT, str(current_user.id), sub_path)
    _ensure_dir(physical_dir)
    physical_path = os.path.join(physical_dir, generated_name)

    # Guardar el archivo en disco
    with open(physical_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Persistir registro en BD
    attachment = Attachment(
        user_id=current_user.id,
        entity_type=entity_type,
        entity_id=entity_id,
        original_filename=original_name,
        generated_filename=generated_name,
        file_path=physical_path,
        directory_id=directory_id,
        mime_type=file.content_type
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment


@router.delete("/{id}")
def delete_attachment(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    attachment = db.get(Attachment, id)
    if not attachment or attachment.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    # Soft delete
    attachment.deleted_at = datetime.utcnow()
    db.add(attachment)
    db.commit()
    return {"status": "success", "message": "Archivo eliminado de la bóveda"}
