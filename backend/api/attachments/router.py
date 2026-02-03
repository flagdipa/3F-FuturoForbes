"""
API Router for Attachments (Adjuntos)
Provides file upload and polymorphic attachment management
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from typing import List, Optional
from pathlib import Path
import shutil
import os
from datetime import datetime
from backend.core.database import get_session
from backend.models.models_extended import Adjunto
from .schemas import AdjuntoCreate, AdjuntoResponse, AdjuntoUpdate

router = APIRouter(prefix="/attachments", tags=["Attachments"])

# Configuration
UPLOAD_DIR = Path("uploads/attachments")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


# ==================== ATTACHMENTS CRUD ====================

@router.post("/", response_model=AdjuntoResponse, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    tipo_referencia: str,
    id_referencia: int,
    descripcion: str = None,
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    """Upload a file attachment for any entity"""
    
    # Validate file size
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Archivo demasiado grande. Máximo: {MAX_FILE_SIZE // 1024 // 1024}MB"
        )
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = UPLOAD_DIR / safe_filename
    
    # Save file
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar archivo: {str(e)}")
    
    # Create database record
    adjunto = Adjunto(
        tipo_referencia=tipo_referencia,
        id_referencia=id_referencia,
        descripcion=descripcion,
        nombre_archivo=file.filename,
        ruta_archivo=str(file_path),
        tipo_mime=file.content_type,
        tamaño_bytes=file_size
    )
    
    session.add(adjunto)
    session.commit()
    session.refresh(adjunto)
    
    return adjunto


@router.get("/{tipo_referencia}/{id_referencia}", response_model=List[AdjuntoResponse])
def list_entity_attachments(
    tipo_referencia: str,
    id_referencia: int,
    session: Session = Depends(get_session)
):
    """List all attachments for a specific entity"""
    query = select(Adjunto).where(
        Adjunto.tipo_referencia == tipo_referencia,
        Adjunto.id_referencia == id_referencia
    ).order_by(Adjunto.fecha_creacion.desc())
    
    attachments = session.exec(query).all()
    return attachments


@router.get("/download/{id_adjunto}")
def download_attachment(id_adjunto: int, session: Session = Depends(get_session)):
    """Download an attachment file"""
    adjunto = session.get(Adjunto, id_adjunto)
    if not adjunto:
        raise HTTPException(status_code=404, detail="Adjunto no encontrado")
    
    file_path = Path(adjunto.ruta_archivo)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado en disco")
    
    return FileResponse(
        path=file_path,
        filename=adjunto.nombre_archivo,
        media_type=adjunto.tipo_mime or "application/octet-stream"
    )


@router.put("/{id_adjunto}", response_model=AdjuntoResponse)
def update_attachment(
    id_adjunto: int,
    adjunto_data: AdjuntoUpdate,
    session: Session = Depends(get_session)
):
    """Update attachment metadata (description only)"""
    adjunto = session.get(Adjunto, id_adjunto)
    if not adjunto:
        raise HTTPException(status_code=404, detail="Adjunto no encontrado")
    
    if adjunto_data.descripcion is not None:
        adjunto.descripcion = adjunto_data.descripcion
        adjunto.fecha_actualizacion = datetime.utcnow()
    
    session.add(adjunto)
    session.commit()
    session.refresh(adjunto)
    return adjunto


@router.delete("/{id_adjunto}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attachment(id_adjunto: int, session: Session = Depends(get_session)):
    """Delete an attachment (file and database record)"""
    adjunto = session.get(Adjunto, id_adjunto)
    if not adjunto:
        raise HTTPException(status_code=404, detail="Adjunto no encontrado")
    
    # Delete file from disk
    file_path = Path(adjunto.ruta_archivo)
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception as e:
            print(f"Warning: Could not delete file {file_path}: {e}")
    
    # Delete database record
    session.delete(adjunto)
    session.commit()
    return None
