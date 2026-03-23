## 1. Local OCR Endpoint Testing
- [x] 1.1 Localizar o verificar el middleware/plugin OCR en `/backend/api/v1` o donde se registren.
- [x] 1.2 Confirmar si PaddleOCR endpoint está levantando en `/api/ia/ocr` (o equivalente V2).

## 2. UI Upload Integration 
- [x] 2.1 Modificar el manejador web `transaction-form.js` o modal HTML para crear método asíncrono `scanReceipt(file)`.
- [x] 2.2 Vincular evento HTML UI del input de cámara/documento (`<input type='file'>`) para llamar el método correspondiente.

## 3. UI State Binding & UX
- [x] 3.1 Introducir variables booleanas `isScanningReceipt = true` al store principal del formulario de transacciones.
- [x] 3.2 Visualizar un spinner de carga y mensaje 'Analizando...' que bloquee el botón de 'Guardar' o 'Cancelar' durante la espera (~2 a 10s).
- [x] 3.3 Lanzar NotificationManager error desde catch si algo falla interrumpiendo el flujo.

## 4. Parser & Field Mapping
- [x] 4.1 Capturar JSON response (`fetch / Axios`) de los datos escaneados.
- [x] 4.2 Mapear campos detectados (`merchant`, `date`, `total_amount`) en las variables reactivas de la UI (`store.payee = ` , `store.amount = `, `store.date = `).
- [x] 4.3 Actualizar `estado_proyecto.md` moviendo la tarea 7 de la fase de Prioridad MEDIA a COMPLETADA.
