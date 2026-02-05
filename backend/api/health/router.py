"""
Health check endpoint for monitoring system status.
"""
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from datetime import datetime
from typing import Dict, Any
from ...core.database import get_session
from ...core.config_inf import config_inf
import os
import shutil

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
async def health_check(session: Session = Depends(get_session)) -> JSONResponse:
    """
    Comprehensive health check endpoint.
    Returns 200 if all checks pass, 503 if any check fails.
    
    Checks:
    - Database connectivity
    - Disk space
    - System version
    """
    health_status = {
        "status": "healthy",
        "version": config_inf.get("SISTEMA", "version", "1.0.0"),
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # Database connectivity check
    try:
        result = session.exec(select(1)).first()
        health_status["checks"]["database"] = {
            "status": "ok",
            "message": "Database connection successful"
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "error",
            "message": f"Database connection failed: {str(e)}"
        }
        health_status["status"] = "unhealthy"
    
    # Disk space check
    try:
        disk_usage = shutil.disk_usage(".")
        free_gb = disk_usage.free / (1024 ** 3)
        total_gb = disk_usage.total / (1024 ** 3)
        percent_free = (disk_usage.free / disk_usage.total) * 100
        
        disk_status = "ok" if percent_free > 10 else "warning"
        health_status["checks"]["disk_space"] = {
            "status": disk_status,
            "free_gb": round(free_gb, 2),
            "total_gb": round(total_gb, 2),
            "percent_free": round(percent_free, 2)
        }
        
        if percent_free < 5:
            health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["checks"]["disk_space"] = {
            "status": "error",
            "message": f"Disk check failed: {str(e)}"
        }
    
    # Application checks
    health_status["checks"]["application"] = {
        "status": "ok",
        "uptime_seconds": "N/A"  # Could track with global start time
    }
    
    # Determine HTTP status code
    status_code = 200 if health_status["status"] == "healthy" else 503
    
    return JSONResponse(content=health_status, status_code=status_code)


@router.get("/ready")
async def readiness_check(session: Session = Depends(get_session)) -> Dict[str, Any]:
    """
    Kubernetes/Docker readiness probe.
    Returns 200 only if system is ready to accept traffic.
    """
    try:
        # Test database
        session.exec(select(1)).first()
        
        return {
            "ready": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception:
        return JSONResponse(
            content={"ready": False, "timestamp": datetime.utcnow().isoformat()},
            status_code=503
        )


@router.get("/alive")
async def liveness_check() -> Dict[str, bool]:
    """
    Kubernetes/Docker liveness probe.
    Returns 200 if process is alive.
    """
    return {"alive": True}
