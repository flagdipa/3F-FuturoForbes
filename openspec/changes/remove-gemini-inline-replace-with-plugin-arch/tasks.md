# Tasks: Remove Inline Gemini API — Replace with IA Plugin Architecture

## 1. Eliminar gemini_engine.py y sus referencias
- [x] 1.1 Eliminar el archivo `backend/plugins/ia_ocr/gemini_engine.py`.
- [x] 1.2 En `backend/api/v1/ia.py`, revertir el endpoint `POST /ocr` al comportamiento original: solo llama a `ocr_service.process_image()` sin bloque de fallback Gemini inline.

## 2. Limpiar Configuración
- [x] 2.1 En `backend/core/config.py`, eliminar los campos `GEMINI_API_KEY` y `GOOGLE_AI_API_KEY` de la clase `Settings`.
- [x] 2.2 En `.env.example`, eliminar o comentar las líneas referentes a `GEMINI_API_KEY` y `GOOGLE_AI_API_KEY`. Agregar una nota indicando que la integración de IA cloud se realiza mediante plugins.

## 3. Definir Interfaz de Plugin IA
- [x] 3.1 Crear el archivo `backend/plugins/base_ia.py` con la clase abstracta `IAProviderPlugin` que define los métodos `is_configured()` y `analyze_receipt(image_bytes, mime_type)`.

## 4. Documentar Contrato de Plugin IA
- [x] 4.1 Crear el archivo `docs/ia-plugin-contract.md` documentando la interfaz `IAProviderPlugin`, el formato de respuesta esperado, y un ejemplo mínimo de implementación para guiar a futuros desarrolladores.

## 5. Validar
- [x] 5.1 Ejecutar `pytest backend/tests/` y confirmar que los 15 tests pasan sin errores.
- [x] 5.2 Verificar que el endpoint `POST /api/ia/ocr` con una imagen falsa responde 500 con el mensaje "Ningún motor de OCR disponible..." y no intenta llamar a ninguna API externa.
