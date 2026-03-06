from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlmodel import Session
from ...dependencies import get_db
from ...core.report_service import ReportService
import logging

logger = logging.getLogger("api_reports")
router = APIRouter()

@router.get("/cashflow")
def get_cashflow(
    date_from: datetime = Query(default_factory=lambda: datetime(2024, 1, 1)),
    date_to: datetime = Query(default_factory=datetime.now),
    db: Session = Depends(get_db)):
    """Obtiene el informe de flujos de efectivo en el período."""
    service = ReportService(db)
    return service.get_cashflow_report(1, date_from, date_to)

@router.get("/categories")
def get_categories(
    date_from: datetime = Query(default_factory=lambda: datetime(2024, 1, 1)),
    date_to: datetime = Query(default_factory=datetime.now),
    db: Session = Depends(get_db)):
    """Distribución de gastos por categoría."""
    service = ReportService(db)
    return service.get_category_distribution(1, date_from, date_to)

@router.get("/heatmap")
def get_heatmap(
    date_from: datetime = Query(default_factory=lambda: datetime(2024, 1, 1)),
    date_to: datetime = Query(default_factory=datetime.now),
    db: Session = Depends(get_db)):
    """Mapa de calor de actividad financiera según hora y día."""
    service = ReportService(db)
    return service.get_spending_heatmap(1, date_from, date_to)

@router.get("/net-worth")
def get_net_worth(
    date_from: datetime = Query(default_factory=lambda: datetime(2023, 1, 1)),
    date_to: datetime = Query(default_factory=datetime.now),
    db: Session = Depends(get_db)):
    """Evolución del patrimonio neto."""
    service = ReportService(db)
    return service.get_net_worth_trend(1, date_from, date_to)

@router.get("/budget")
def get_budget_status(
    month: str = Query(default="2024-03"),
    db: Session = Depends(get_db)):
    """Presupuestado vs Ejecutado."""
    service = ReportService(db)
    return service.get_budget_vs_actual(1, month)

@router.post("/export")
def export_report(format: str = Query(..., description="pdf o excel"), db: Session = Depends(get_db)):
    """Genera exportación en background y devuelve un link. (Mock)."""
    return {"message": f"Exportación a {format} en proceso", "link": f"/downloads/report.{format}"}
