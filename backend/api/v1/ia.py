from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlmodel import Session
from sqlmodel import select
from typing import Dict, Any, List

from ...dependencies import get_db

router = APIRouter()

@router.post("/ocr", summary="Analiza un ticket subido por el usuario")
async def analyze_receipt(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Subida de imagen de un ticket/factura para procesarlo vía PaddleOCR, Gemini o Tesseract
    y sugerir los items a cargar como Transacción.
    """
    if not (file.content_type.startswith('image/') or file.content_type == 'application/pdf'):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen o PDF.")
        
    try:
        contents = await file.read()
        
        # Import the plugin service directly to utilize the fallback chain
        from ...plugins.ia_ocr.services import ocr_service
        analysis_result = await ocr_service.process_image(contents, file.content_type)
        
        if analysis_result.get("engine") == "none" and "error" in analysis_result:
             raise HTTPException(status_code=500, detail=analysis_result["error"])
        return analysis_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast", summary="Cashflow predictivo")
async def get_forecasting(months: int = 3, db: Session = Depends(get_db)):
    """
    Devuelve la predicción de Cashflow usando IA basada en el historial del usuario.
    [Offline Mode - Pendiente de Plugin]
    """
    return {
        "predicted_income": [0, 0, 0],
        "predicted_expenses": [0, 0, 0],
        "anomalies_detected": [],
        "recommendations": ["Motor de proyección en mantenimiento o pendiente de plugin IA."],
        "status": "offline"
    }

@router.get("/insights", summary="Observaciones y sugerencias rápidas")
async def get_financial_insights(db: Session = Depends(get_db)):
    """
    Petición rápida al dashboard para mostrar Insights relevantes generados por IA.
    [Offline Mode - Pendiente de Plugin]
    """
    return [
        {
            "type": "info", 
            "title": "Motor IA Analítico Inactivo", 
            "desc": "Este modelo está funcionando en modo sin conexión hasta que configures un nuevo Plugin de Inteligencia Artificial."
        }
    ]
