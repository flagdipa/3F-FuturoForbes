# Tasks: OCR Restoration with Pytesseract

## 1. Configuración de Entorno y Dependencias
- [x] 1.1 Validar instalación de `pytesseract` y `Pillow` en el entorno de Python.
- [x] 1.2 Añadir `TESSERACT_CMD` al archivo `.env` apuntando a `C:\Program Files\Tesseract-OCR\tesseract.exe`.
- [x] 1.3 Actualizar `backend/config.py` para cargar `settings.TESSERACT_CMD` de forma segura.

## 2. Limpieza de Gemini y Fondeo de Tesseract en Core
- [x] 2.1 Eliminar el import de `google-generativeai` y toda referencia a `gemini-1.5-flash` del archivo `backend/plugins/ia_ocr/services.py`.
- [x] 2.2 Reemplazar el método privado `_process_with_gemini` por un robustecido `_process_with_tesseract`.
- [x] 2.3 Quitar el check de `GEMINI_API_KEY` de la inicialización y poner el de Tesseract binario `os.path.exists(TESSERACT_CMD)`.

## 3. Implementación de Heurísticas de Extracción (Regex)
- [x] 3.1 Mejorar el método `_extract_amount_from_text` para manejar separadores de miles y decimales de LATAM (".", ",").
- [x] 3.2 Melhorar el método `_extract_date_from_text` para normalizar fechas al formato ISO `YYYY-MM-DD`.
- [x] 3.3 El campo `establecimiento` debe tomar la primera línea con contenido alfanumérico significativo.

## 4. Pruebas y Validación (End-to-End)
- [x] 4.1 Subir un ticket de prueba (imagen PNG o JPG) al endpoint `POST /api/v1/ia/ocr` (vía postman o una herramienta CLI).
- [x] 4.2 Validar que el campo `engine` del JSON resulte en `"tesseract"` si PaddleOCR no es invocado o falla.
- [x] 4.3 Actualizar `estado_proyecto.md` y marcar el OCR con Tesseract como `COMPLETADO` en la tabla de funcionalidades.
