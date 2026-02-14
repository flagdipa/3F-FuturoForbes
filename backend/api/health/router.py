"""
Health check endpoint for monitoring system status.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from datetime import datetime
from typing import Dict, Any
from pathlib import Path
from ...core.database import get_session
from ...core.config_inf import config_inf
from ..auth.deps import get_current_user
import os
import shutil

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
async def health_check(session: Session = Depends(get_session)) -> JSONResponse:
    """
    Detailed system health check.
    """
    health_status = {
        "status": "healthy",
        "version": config_inf.get("SISTEMA", "version", "1.0.0"),
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # DB Size
    try:
        db_path = "futuroforbes.db"
        if os.path.exists(db_path):
            db_size = os.path.getsize(db_path) / (1024 * 1024)
            health_status["checks"]["database_size_mb"] = round(db_size, 2)
    except: pass

    # File counts
    try:
        attach_dir = Path("uploads/attachments")
        if attach_dir.exists():
            health_status["checks"]["attachments_count"] = len(list(attach_dir.glob("*")))
    except: pass

    # Existing checks... (simplified for space, but keeping logic)
    try:
        session.exec(select(1)).first()
        health_status["checks"]["database"] = {"status": "ok"}
    except: health_status["status"] = "unhealthy"

    # Disk Space
    try:
        usage = shutil.disk_usage(".")
        health_status["checks"]["disk"] = {
            "free_gb": round(usage.free / (1024**3), 2),
            "percent": round((usage.free / usage.total)*100, 1)
        }
    except: pass

    return JSONResponse(content=health_status)

@router.post("/backup")
async def trigger_backup(current_user: Any = Depends(get_current_user)):
    """Triggers a manual database backup"""
    from ...scripts.backup_database import DatabaseBackup
    try:
        manager = DatabaseBackup()
        path = manager.create_backup()
        return {"status": "success", "message": f"Backup created: {path.name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/integrity")
async def run_integrity_check(current_user: Any = Depends(get_current_user), session: Session = Depends(get_session)):
    """Runs a PRAGMA integrity_check (SQLite)"""
    try:
        from sqlalchemy import text
        result = session.execute(text("PRAGMA integrity_check")).fetchone()
        report = "OK" if result[0] == "ok" else result[0]
        return {"status": "success", "report": report}
    except Exception as e:
        return {"status": "error", "message": str(e)}
@router.post("/test-mail")
async def test_mail(data: Dict[str, str], current_user: Any = Depends(get_current_user)):
    """Sends a test email to verify SMTP settings"""
    from ...core.mail_utils import send_email
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Falta el correo destinatario")
    
    success = send_email(
        to_email=email,
        subject="3F SYSTEM | Prueba de Conexión SMTP",
        html_content=f"<h1>Conexión Exitosa</h1><p>Esta es una prueba del sistema FuturoForbes (3F).<br>Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>"
    )
    
    if success:
        return {"status": "success", "message": "Email enviado correctamente"}
    else:
        raise HTTPException(status_code=500, detail="Fallo al enviar email. Revise la consola para detalles.")
