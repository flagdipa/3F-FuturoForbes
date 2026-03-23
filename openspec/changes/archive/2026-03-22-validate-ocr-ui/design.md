## Context
El sistema tiene un motor OCR (PaddleOCR) funcionando localmente bajo Python 3.13 en el servidor, y expuesto mediante una ruta de la API (`/api/ia/ocr` o el router de plugins correspondiente). Sin embargo, en el frontend (el formulario de transacciones / main_form.html o un modal de subida de tickets), la lógica Javascript de "subir ticket", conectarse al backend V2 y rellenar automáticamente los campos (fecha, monto, etc.) no ha sido debidamente integrada ni validada en un flujo End-To-End.

## Goals / Non-Goals
**Goals:**
- Identificar y conectar el endpoint de OCR del plugin `ia_ocr` a la UI de carga de transacciones.
- Proveer Feedback visual interactivo (loading/spinner) durante el proceso de escaneo.
- Parsear y mapear la respuesta del modelo JSON del servidor hacia los stores de estado del frontend (ej. `benefForm` o equivalente si es factura, o `transactionForm` directamente).
- Probar el flujo completo subiendo una factura o ticket de muestra.

**Non-Goals:**
- Actualizar el modelo V2 de base de datos (no se ven afectados al ser una tarea UI/UX).
- Alterar el corazón de procesamiento interno e IA de PaddleOCR o incluir Gemini en esta iteración. Solo la integración UI.

## Decisions
**Decisión 1: Integración con Frontend (Alpine o Fetch V2)**:
Implementar en el Manager de Transacciones (`transaction-form.js` o similar) el método asincrónico `scanReceipt(file)` que interactúe por fetch (o la abstracción `api.post`) contra la ruta detectada bajo `/api/ia/ocr`.

**Decisión 2: Manejo de UX de Larga Duración**:
El parseo local OCR toma de 2s a 10s dependiendo de resolución. Se deberá bloquear el botón "Guardar" y mostrar texto como "Analizando Ticket con OCR...".

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Tiempos de respuesta causan cierres del form por el usuario impulsivo | Pantalla de carga semi-transparente sobre modal o boton deshabilitado con spinner |
| OCR retorna "Costo: OO.OO" | Mostrar un toast notificando al usuario que debe revisar todos los valores extraídos antes de guardar |
