## Why

En el registro de `estado_proyecto.md`, sección de próximos pasos (Prioridad MEDIA - Tarea 7), se requiere validar la funcionalidad de OCR en la interfaz de usuario. Actualmente, el motor OCR local (PaddleOCR) inicializa correctamente en el backend (Python 3.13), y el endpoint existe (`/api/ia/ocr`), pero la integración en la UI no ha sido probada de extremo a extremo (subir imagen → auto-completado del formulario). Asegurar que esto funcione es clave para automatizar la carga de comprobantes.

## What Changes

- Validar la subida de imágenes desde la interfaz web al backend de OCR.
- Conectar la respuesta JSON del motor OCR para auto-rellenar los campos del formulario de creación de transacciones.
- Asegurarse de que el frontend está interactuando con las nuevas rutas V2 (ej. `/api/v1/ocr` o plugins, validando la ruta correcta).
- Implementar manejo de errores si la extracción de texto falla o la imagen es ilegible.

## Capabilities

### New Capabilities
- Carga de imágenes para extracción automática de datos (fecha, monto, beneficiario).

### Modified Capabilities
- Formularios de Transacción: Se añadirán/revisarán los handlers JavaScript para la carga de comprobantes mediante fetch/XHR hacia el plugin de OCR.

## Impact

- **Frontend**: `frontend/templates/transacciones.html`, scripts JavaScript asociados (posiblemente `frontend/static/js/transaction-form.js`).
- **Backend**: Verificación rápida de la ruta OCR (`backend/plugins/ia_ocr/` y routers de fastapi) para confirmar que acepta y responde con los formatos adecuados para V2.
- **Flujo UX**: Experiencia fluida al añadir transacciones a partir de tickets.
