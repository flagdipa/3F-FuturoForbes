# Tasks: Verificación E2E Automatizada

## 1. Configuración del Marco de Pruebas
- [ ] 1.1 Verificar la instalación de Playwright en `frontend/package.json` y dependencias asociadas.
- [ ] 1.2 Configurar archivo de log de Playwright para escribir incidencias de Consola de JS (AlpineJS/Frontend bugs) y de Red (Status >= 400 Backend bugs). 

## 2. Desarrollo de Scripts de Flujo (Agentes/Fases)
- [ ] 2.1 Fase de **Autenticación**: Crear un test que cargue `http://localhost:8000`, efectúe un login o indique error de token.
- [ ] 2.2 Fase de **Catalogos y Cuentas**: Test secuencial que corra el CRUD sobre `/accounts`, `/payees` y `/categories` capturando cualquier problema del DOM.
- [ ] 2.3 Fase de **Operativa Core (Transacciones)**: Test de alta de ingreso simple, alta de gasto con split y simulación de adjunto OCR.
- [ ] 2.4 Fase de **Herramientas**: Añadir pruebas superficiales en `/budgets` (Presupuestos) y `/goals` (Metas de Ahorro).

## 3. Ejecución de la Verificación Activa
- [ ] 3.1 Arrancar el servidor backend vía `python -m uvicorn backend.main:app` (en otra pestaña o script local).
- [ ] 3.2 Ejecutar la consola interactiva test (Playwright): `cd frontend && npx playwright test` (o similar) y generar el volcado.

## 4. Consolidación
- [ ] 4.1 Extraer las fallas del test hacia un reporte final MD o txt (ej. `frontend_bug_report.md`) dentro de este spec.
- [ ] 4.2 (Opcional) Proponer soluciones / "hotfixes" inmediatos para el frontend dependiendo de los resultados arrojados por los Agentes en el paso anterior.
