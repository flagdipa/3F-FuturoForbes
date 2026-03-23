# Specs: Remove Inline Gemini API — Replace with IA Plugin Architecture

## BDD Requirements

### Requirement: Eliminar gemini_engine.py
- **GIVEN** que `backend/plugins/ia_ocr/gemini_engine.py` existe en el repositorio
- **WHEN** el cambio se aplica
- **THEN** el archivo es eliminado del filesystem y del historial de git

### Requirement: Endpoint OCR limpio sin fallback inline
- **GIVEN** que el endpoint `POST /api/ia/ocr` recibe una imagen
- **WHEN** PaddleOCR y Tesseract no están disponibles
- **THEN** el endpoint responde con `HTTP 500` y `{ "detail": "Ningún motor de OCR disponible..." }`
- **AND** NO intenta llamar a ninguna API externa de IA
- **AND** NO requiere ninguna API key de Gemini o Google configurada

### Requirement: Config sin credenciales de Gemini
- **GIVEN** que `backend/core/config.py` define los campos de la aplicación
- **WHEN** se revisa el archivo Settings
- **THEN** NO existen los campos `GEMINI_API_KEY` ni `GOOGLE_AI_API_KEY`
- **AND** el campo `TESSERACT_CMD` sigue presente (es configuración local válida)

### Requirement: .env.example limpio
- **GIVEN** que `.env.example` documenta las variables de entorno
- **WHEN** un desarrollador nuevo lo revisa
- **THEN** NO aparecen variables de Gemini ni Google AI
- **AND** aparece una nota explicando que la integración de IA cloud se hace mediante plugins

### Requirement: Interfaz IAProviderPlugin definida
- **GIVEN** que un desarrollador quiere crear un plugin de IA (ej. Gemini, OpenAI)
- **WHEN** revisa `backend/plugins/base_ia.py`
- **THEN** encuentra la clase abstracta `IAProviderPlugin` con métodos `is_configured()` y `analyze_receipt()`
- **AND** la firma de `analyze_receipt()` retorna un dict compatible con el formato que espera el frontend

### Requirement: Tests continúan pasando
- **GIVEN** que la suite de tests en `backend/tests/` existe
- **WHEN** se ejecuta `pytest backend/tests/`
- **THEN** los 15 tests pasan sin errores
- **AND** ningún test depende de Gemini o de `gemini_engine.py`

### Requirement: Documentación del contrato de plugin IA
- **GIVEN** que se quiere implementar un plugin Gemini en el futuro
- **WHEN** se consulta `docs/ia-plugin-contract.md`
- **THEN** el documento describe cómo implementar `IAProviderPlugin`
- **AND** incluye un ejemplo mínimo de implementación
- **AND** describe el formato de respuesta esperado (`fecha`, `monto_total`, `establecimiento`, etc.)
