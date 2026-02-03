from fastapi import APIRouter, UploadFile, File, HTTPException
from ...core.ia_service import ia_service
import json

router = APIRouter(prefix="/ia", tags=["Inteligencia Artificial"])

@router.post("/escanear-ticket")
async def escanear_ticket(file: UploadFile = File(...)):
    """
    Sube una imagen de un ticket y usa Gemini para extraer los datos financieros.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")

    content = await file.read()
    resultado = await ia_service.procesar_ticket(content, file.content_type)
    
    if isinstance(resultado, dict) and "error" in resultado:
        raise HTTPException(status_code=500, detail=resultado["error"])
    
    try:
        # Intentar parsear el JSON retornado por la IA
        data = json.loads(resultado)
        return data
    except Exception as e:
        return {"raw_response": resultado, "error": "No se pudo parsear el JSON de la IA"}
