# Proposal: Remove Inline Gemini API — Replace with IA Plugin Architecture

## Problem Context

Durante el cambio `tech-debt-tests-ocr-fallback` se implementó un fallback de Gemini Vision directamente en el código de producción del endpoint `/api/ia/ocr` y en el módulo `backend/plugins/ia_ocr/gemini_engine.py`. Si bien el fallback funciona, este enfoque **introduce deuda arquitectónica**:

1. **Acoplamiento directo**: La API de Gemini está cableada dentro del motor OCR local, en lugar de ser un plugin intercambiable.
2. **Credenciales hardcodeadas en config global**: `GEMINI_API_KEY` y `GOOGLE_AI_API_KEY` están en `backend/core/config.py` como campos de aplicación, cuando deberían ser configuración de plugin.
3. **Privacidad y usuario control**: El usuario no puede decidir "quiero activar/desactivar Gemini" desde la UI, ni ver su consumo.
4. **Inconsistencia con la arquitectura de plugins**: El sistema ya tiene un `Plugin Manager` (`backend/plugins/`) diseñado para inyectar capacidades opcionales. Gemini debería entrar por ahí.
5. **Riesgo de futuros conflictos**: Si se agrega un segundo proveedor de IA (OpenAI, Anthropic), no hay un patrón claro de cómo extenderlo sin duplicar código.

## Proposed Solution

Eliminar todas las referencias inline a Gemini del código core y preparar la arquitectura para que los proveedores de IA (Gemini, OpenAI, etc.) se integren exclusivamente como **plugins activables desde la UI**:

1. **Eliminar `gemini_engine.py`** del módulo `ia_ocr` y toda referencia a él en `ia.py`.
2. **Eliminar `GEMINI_API_KEY` y `GOOGLE_AI_API_KEY`** de `backend/core/config.py`.
3. **Restaurar `ia.py`** a su comportamiento original: OCR local → Tesseract fallback → error 500 elegante.
4. **Definir la interfaz `IAProviderPlugin`** como contrato formal que futuros plugins de IA deberán implementar.
5. **Documentar el patrón**: Crear `docs/ia-plugin-contract.md` con la especificación de cómo crear un plugin de IA (para cuando se implemente Gemini como plugin real).

## Impact

- **Archivos eliminados**: `backend/plugins/ia_ocr/gemini_engine.py`
- **Archivos modificados**: `backend/api/v1/ia.py`, `backend/core/config.py`, `.env.example`
- **Sin cambios en frontend**: El endpoint `/api/ia/ocr` mantiene su respuesta idéntica.
- **Sin cambios en tests**: Los tests actuales no dependen de Gemini.
- **Sin regresiones**: El OCR local (Tesseract/PaddleOCR) continúa funcionando exactamente igual.
