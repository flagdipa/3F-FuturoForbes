# Specs: Tests Restoration & Gemini OCR Fallback

## BDD Requirements

### Requirement: Pytest Test Suite
- **GIVEN** un entorno python testeable (preferiblemente con variables `.env.test`)
- **WHEN** el programador ejecuta `pytest backend/tests/`
- **THEN** la colección debe ubicar `test_transactions_api.py`, `test_accounts_api.py`, `test_budgets_api.py` (Mínimo Core).
- **AND THEN** inyecta base de datos SQLite efímera.
- **AND THEN** 100% PASS sin errores persistentes (e.g. tablas ocupadas o bloqueos).

### Requirement: Gemini Fallback on Invalid Image
- **GIVEN** que existe una validación OCR local y se setea `GEMINI_API_KEY` en environment
- **WHEN** un usuario sube un comprobante via `/api/ia/ocr` que rompe el Motor Paddle (Exception arrojada) O si el usuario pide proactivamente usar Cloud.
- **THEN** la imagen original es capturada, validada y enviada a `models/gemini-1.5-flash` o `gemini-2.5-flash`.
- **AND THEN** Google la parsea en JSON.
- **AND THEN** FastAPI la formatea regresando el idéntico layout `{ "amount":..., "date":... }` que el Engine local al cliente web, evitando que el crasheo sea público.

### Requirement: Exclusión de Gemini si no hay key
- **GIVEN** un crasheo del PaddleOCR
- **WHEN** `GEMINI_API_KEY` es omitido en el `.env` (o está nulo/vacío)
- **THEN** el Except capta el nulo y devuelve un error 500 elegante `{"detail": "OCR Local falló. Gemini Fallback no configurado."}` al panel HTTP que le advierta al usuario del problema.
