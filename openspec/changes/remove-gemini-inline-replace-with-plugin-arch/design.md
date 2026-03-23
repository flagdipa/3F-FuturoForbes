# Design: Remove Inline Gemini API — Replace with IA Plugin Architecture

## Context

El sistema 3F tiene un `Plugin Manager` (`backend/plugins/`) que permite activar/desactivar capacidades opcionales desde una UI de administración. Sin embargo, el fallback de Gemini Vision fue implementado directamente en el código core del endpoint OCR durante el sprint anterior, saltando esta arquitectura. Este diseño detalla cómo revertir eso limpiamente y sentar las bases para una futura integración formal de proveedores IA como plugins.

## Goals / Non-Goals

### Goals
- Eliminar toda referencia a `google-genai`, `GEMINI_API_KEY`, y `gemini_engine.py` del código de producción core.
- Dejar `backend/api/v1/ia.py` limpio: solo llama a `ocr_service.process_image()` — sin fallback cloud inline.
- Limpiar `backend/core/config.py` removiendo los campos de Gemini.
- Definir una interfaz abstracta `IAProviderPlugin` que los futuros plugins de IA deberán implementar.
- Documentar el contrato de plugin IA para referencia futura.

### Non-Goals
- Implementar el plugin de Gemini como plugin real (eso va en un change futuro).
- Cambiar el comportamiento de PaddleOCR o Tesseract.
- Modificar el frontend.

## Technical Approach

### 1. Archivos a Eliminar
- `backend/plugins/ia_ocr/gemini_engine.py` — clase wrapper en el lugar incorrecto.

### 2. Modificaciones en `backend/api/v1/ia.py`
Revertir el endpoint `POST /ia/ocr` a su comportamiento original y limpio:
```python
@router.post("/ocr")
async def analyze_receipt(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not (file.content_type.startswith('image/') or file.content_type == 'application/pdf'):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen o PDF.")
    try:
        contents = await file.read()
        from ...plugins.ia_ocr.services import ocr_service
        result = await ocr_service.process_image(contents, file.content_type)
        if result.get("engine") == "none" and "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 3. Limpiar `backend/core/config.py`
Eliminar los campos:
- `GOOGLE_AI_API_KEY`
- `GEMINI_API_KEY`

Mantener solo el campo `TESSERACT_CMD` (uso legítimo del motor local).

### 4. Actualizar `.env.example`
Eliminar las líneas referentes a `GEMINI_API_KEY` y `GOOGLE_AI_API_KEY`.

### 5. Definir `IAProviderPlugin` interface
Crear `backend/plugins/base_ia.py` con la interfaz abstracta:
```python
from abc import ABC, abstractmethod

class IAProviderPlugin(ABC):
    """Contrato para plugins de IA proveedores de servicios cognitivos."""
    
    @abstractmethod
    def is_configured(self) -> bool:
        """Returns True si el plugin tiene credenciales y está listo."""
        ...
    
    @abstractmethod
    async def analyze_receipt(self, image_bytes: bytes, mime_type: str) -> dict:
        """Analiza una imagen de ticket y devuelve datos financieros estructurados."""
        ...
```

### 6. Crear `docs/ia-plugin-contract.md`
Documentar el patrón para futuros implementadores (ej. plugin Gemini, plugin OpenAI), incluyendo:
- La interfaz que deben implementar
- El formato de respuesta esperado
- Cómo registrar el plugin en el Plugin Manager
- Ejemplo mínimo de implementación

## Risks / Trade-offs
- **Sin riesgos funcionales**: El OCR local (Tesseract/PaddleOCR) no se toca.
- **Los tests siguen pasando**: Ningún test depende de `gemini_engine.py`.
- **Pérdida temporal de fallback cloud**: Si un ticket no puede ser procesado localmente, no habrá fallback cloud hasta que se implemente el plugin. Esto es **aceptado conscientemente** por el usuario.
