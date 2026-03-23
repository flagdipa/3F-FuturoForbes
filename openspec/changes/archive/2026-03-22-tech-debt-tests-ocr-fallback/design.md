# Design: Tests Restoration & Gemini OCR Fallback

## Context
Tras los masivos cambios arquitectónicos durante el pasaje a "Arquitectura Definitiva V2" (SQLModel y HUD Neon), parte de la seguridad de la refactorización dependía de un testeo ciego semi-manual o scripts locales. Los endpoints de `backend/api/v1/` están sirviendo JSON Pydantic nativo, abandonando los diccionarios pre-formateados estilo V1. A nivel OCR, `backend/api/v1/ia.py` ya lee eficientemente los tickets gracias al plugin local, logrando subir la transacción escaneada al UI. Sin embargo, no estamos abarcando el caso borde en el que dicho plugin colapse por un comprobante dañado o sin texto identificable válido, haciendo fracasar la experiencia del usuario.

## Goals / Non-Goals
### Goals
- Estabilizar pytest corriendo `pytest backend/tests` obteniendo de manera consistente `100% Pass` en al menos tests vitales (Cuentas, Transacciones, Categorías).
- Un `conftest.py` en entorno efímero (`sqlite3 :memory:` idealmente) que levante limpiamente los esquemas `Base.metadata.create_all()` y configure un `client = TestClient(app)`.
- El endpoint `POST /api/ia/ocr` deberá invocar al proveedor OCR Local y en bloque `try...except`, derivar a la `google-genai` pip library con un Prompt Zero-Shot validado estricto retornando `JSON`.

### Non-Goals
- Sustituir totalmente PaddleOCR por Gemini. El procesamiento local es primordial por privacidad y velocidad. Gemini es puramente un Fail-Safe / Fallback.
- Pruebas E2E de Node.js o Selenium. Se apuntará 100% a la cobertura de API V2.

## Technical Approach

### 1. Pytest V2 Restoration (`conftest.py` + tests)
Toda batería de pruebas moderna en FastAPI exige inyección de dependencias `app.dependency_overrides[get_db] = override_get_db`.
1. Crear `testing.db` o entorno de test temporal, inicializándolo con `SQLModel.metadata.create_all(bind=engine)`.
2. Generar un `session_fixture`.
3. Crear un bloque `test_transactions.py` insertando por test_client `POST /api/transactions/` validando campos específicos. 
4. Si las llamadas fallan, corregir el código del test o de la App (depende del bug).

### 2. Gemini Fallback (`api/v1/ia.py` y `plugins`)
En `backend/api/v1/ia.py` el handler `procesar_ocr_ticket(file)` invoca a `ocr_engine.extract_text(temp_path)`. Aquí rodearemos esto en `try ... except Exception as e`, y si falla:
1. Validar que exista la librería de google genai y el `os.environ.get("GEMINI_API_KEY")`. Si no, re-lanzar error original.
2. Hacer POST subiendo la imagen en `base64` a Gemini 1.5 Flash o Gemini 2.0 Flash (los más rápidos).
3. Utilizar "Prompting for JSON format": 
   `"Extract receipt information and return ONLY valid JSON with keys: amount(float), date(YYYY-MM-DD), description(string), payee(string). Do not use markdown backticks."`
4. Parsear el `response.text` con `json.loads` y retornar payload simulando que todo anduvo de forma normal.

## Risks / Trade-offs
- **Dependencia de Red**: Usar Gemini exigirá latencia de subida y llamadas REST intercontinentales (3-5 segundos vs <1 segundo OCR local). Se asume tolerable bajo la bandera "peor es no leer el ticket".
- **Limpieza BD**: `conftest.py` con DB persistente pero descartable como `test.db` suele enclavar threads si no usamos `check_same_thread=False` y generamos correctos teardowns. Optar por DBs efímeras.
