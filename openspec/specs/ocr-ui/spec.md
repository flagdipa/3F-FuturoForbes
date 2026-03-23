# OCR UI Integration Spec

## BDD Requirements

### Requirement: Capturar datos de factura o comprobante mediante OCR local
- **GIVEN** que el usuario abre el modal de formulario de creación o edición de transacciones.
- **WHEN** el usuario hace clic en un botón como 'Analizar Factura' o 'Subir comprobante OCR' y adjunta una imagen o PDF.
- **THEN** la imagen subida debe transmitirse mediante form-data al endpoint de inteligencia artificial `/api/ia/ocr` o el de plugins.
- **AND THEN** el programa activará un estado o indicador visual de 'Loading' impidiendo así que el usuario cierre agresivamente la ventana pensando que no funcionó, lo cual le tomaría entre 2 y 10 segundos al motor OCR.
- **AND THEN** una vez recibida la respuesta JSON (`{"date": "...", "amount": 1000, "merchant": "..."}`), estos campos mapean su valor llenando los del UI (monto total, la fecha detectada, nombre de beneficiario detectado como merchant/payee).

### Requirement: Fallo de motor o archivo ilegible
- **GIVEN** un ticket mal iluminado o el pipeline en el servidor arroja un error temporal (`HTTP 500`).
- **WHEN** se interrumpe la conexión o paddle_engine de OCR no logra extraer ninguna metadata.
- **THEN** el UI debe detener el loader velozmente restaurando el estado interactivo de los inputs.
- **AND THEN** se invocará el framework de notificaciones (e.g. `NotificationManager.error()`) enviando el texto indicando 'No se pudieron extraer datos del comprobante proporcionado'.
