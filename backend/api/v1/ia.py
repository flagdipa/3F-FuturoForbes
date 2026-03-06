from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlmodel import Session
from sqlmodel import select
from typing import Dict, Any, List

from ...dependencies import get_db
from ...core.ia_engine import IAEngine

router = APIRouter()
# We should instance IAEngine once globally or per-request based on app settings
# For simplicity, we initialize it here:
ia_service = IAEngine()  # Assume key load logic is configured via environment later

@router.post("/ocr", summary="Analiza un ticket subido por el usuario")
async def analyze_receipt(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Subida de imagen de un ticket/factura para procesarlo vía Google Gemini 1.5 Flash
    y sugerir los items a cargar como Transacción.
    """
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen.")
        
    try:
        contents = await file.read()
        analysis_result = await ia_service.analyze_receipt(contents)
        return analysis_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast", summary="Cashflow predictivo")
async def get_forecasting(months: int = 3, db: Session = Depends(get_db)):
    """
    Devuelve la predicción de Cashflow usando IA basada en el historial del usuario.
    """
    # En un caso real: obtener data del LedgerEngine para entregar al modelo
    user_tx_mock = [{"type": "EXPENSE", "amount": 1000}, {"type":"INCOME", "amount": 2500}] 
    try:
        forecast = await ia_service.forecast_cashflow(user_tx_mock)
        return forecast
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights", summary="Observaciones y sugerencias rápidas")
async def get_financial_insights(db: Session = Depends(get_db)):
    """
    Petición rápida al dashboard para mostrar Insights relevantes 
    generados con LLMs (Ej: "Ahorraste 15% este mes").
    """
    insights = await ia_service.generate_insights(user_id=1)
    return insights
