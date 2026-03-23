# Tasks: Tests Restoration & Gemini OCR Fallback

## 1. Configurar Entorno Pytest y DB en Memoria (`conftest.py`)
- [x] 1.1 Reescribir `backend/tests/conftest.py` para usar `sqlite:///:memory:` y crear un `Engine` específico usando `StaticPool` de SQLite en Pydantic.
- [x] 1.2 Implementar fixture `session` con yield en `conftest.py`.
- [x] 1.3 Implementar fixture `client` (TestClient de fastapi) usando override de dependency `app.dependency_overrides[get_db] = override_get_db`.

## 2. Refactor y Re-creación de Test Clásicos V2
- [x] 2.1 Crear `backend/tests/test_01_accounts_v2.py` probando `POST /api/v1/accounts/` y validando 200/201 con campos nativos.
- [x] 2.2 Crear `backend/tests/test_02_transactions_v2.py` insertando una transacción V2 compleja con `splits`.
- [x] 2.3 Ejecutar `pytest backend/tests` y confirmar el PASS sin errores subyacentes.

## 3. Gemini OCR Fallback Engine
- [x] 3.1 Instalar o corroborar `google-genai` en Python usando `pip install google-genai`.
- [x] 3.2 Crear en `backend/plugins/ia_ocr/gemini_engine.py` la clase estática envoltorio que use `genai.Client` con el System Prompt para parsear el recibo JSON y reciba bytes de imágen (soporta base64 o raw bytes de FastAPI UploadFile).
- [x] 3.3 Agregar `.env` mapping para `GEMINI_API_KEY`. (Nota: solo si se provee la key, se debe requerir el módulo gemini activado. Fallar graciosamente si no).

## 4. Integrar Fallback en `/api/ia/ocr`
- [x] 4.1 En `backend/api/v1/ia.py`, dentro del endpoint `procesar_ocr_ticket`, envolver la llamada genérica en un `try ... except` e instruir el traspaso a Gemini.
- [x] 4.2 Enviar un file falso para provocar colapso en `paddle_engine.py` (ej imagen negra) y verificar la intervención exitosa de Gemini para leer el fail, o bien forzar timeout.

## 5. Validar Documentación y Limpieza
- [x] 5.1 En `estado_proyecto.md`, mover "Suite de Test" y "Gemini API Key" de MEDIA/Prioridades a "COMPLETADA".
- [x] 5.2 Limpiar importaciones rotas o scripts huerfanos resultantes de los viejos modulos de tests inservibles.
