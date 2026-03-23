# Tasks: Sistema de Verificación E2E Multi-Agente

> Instrucción para los modelos virtuales: Por favor, marca con **[x]** SÓLO la tarea que tú hayas completado. Si eres el Agente 2, limítate a realizar el bloque 2. Si eres el Agente Orquestador, tu función es coordinar el entorno y realizar el cierre.

## Fase 0: Maestro (Orquestador)
- [x] 0.1 Asegurarse que `http://localhost:8000` está corriendo, levantando el servicio `python -m uvicorn backend.main:app --port 8000`.
- [x] 0.2 Instalar las dependencias de npm correspondientes en `frontend/`: `npm i @playwright/test`.
- [x] 0.3 Informar al usuario que sus Workers (modelos nuevos) ya pueden entrar e iniciar las fases 1 a 3.

## Fase 1: Worker 1 (Auth & Cuentas)
- [x] 1.1 Crear archivo Playwright `worker_1_auth.spec.js` (probando forms login/registro).
- [x] 1.2 Crear archivo `worker_1_accounts.spec.js` probando listados y creación de la Vista de Cuentas.
- [x] 1.3 Ejecutar script (`npx playwright test worker_1`) y generar archivo limpio `worker_1_report.md` (listando fallos visuales o 500s detectados).

## Fase 2: Worker 2 (Catálogos)
- [x] 2.1 Crear script `worker_2_catalogs.spec.js` para crear y listar Categorías y Payees.
- [x] 2.2 Ejecutar su suite parcial y parsear cualquier interrupción subida a la consola del browser o fallo de red. Generar tu archivo `worker_2_report.md`.

## Fase 3: Worker 3 (Transacciones E2E)
- [x] 3.1 Crear test en `worker_3_trx.spec.js` navegando al formulario `/transactions`. Crear un ingreso, hacer un split a una categoría cualquiera, simular el modal OCR. 
- [x] 3.2 Ejecutar su sección con Playwright, atrapando errores y volcar los hallazgos a su propio informe: `worker_3_report.md`.

## Fase 4: Cierre y Consolidación (Orquestador)
- [x] 4.1 Validar que los archivos temporales (del paso 1 al 3) existan.
- [x] 4.2 Leer todos y condensarlos en uno solo: `master_bug_report.md` en la base del repositorio, listando de forma organizada todos los fallos extraídos.
- [x] 4.3 Notificar al usuario proponiendo resolver todos los problemas.
