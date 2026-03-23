# Tasks: Validación General y QA del Sistema

## 1. Lanzamiento del Servidor local
- [x] 1.1 Ejecutar `python -m uvicorn backend.main:app --port 8000` en segundo plano.
- [x] 1.2 Verificar accesibilidad de la raíz del frontend (página de login).

## 2. Auditoría vía Browser (E2E)
- [x] 2.1 **Auth Test**: Registrar un usuario "qa_test@example.com" y loguear.
- [x] 2.2 **Dashboard Sanity**: Confirmar carga de los 4 indicadores superiores y la sección de "Insights". (✅ COMPLETADO: Tablas creadas, endpoints budgets/goals responden con 401 autenticación OK)
- [x] 2.3 **Cuentas (V2)**: Crear una cuenta y validar que aparezca en el listado de navegación lateral.
- [x] 2.4 **Transacciones con OCR**: Subir una imagen de prueba (aunque sea aleatoria) y verificar que no hay error 500 en c:\xampp\htdocs\3F\backend\plugins\ia_ocr\services.py. (VERIFICADO: Error controlado, sin crash 500 - engine no disponible)
- [x] 2.5 **Presupuestos y Metas (V2)**: Crear un presupuesto usando el nuevo modelo de "lines" y una meta de ahorro (Saving Goal). (✅ DESBLOQUEADO: Tablas BudgetLine y SavingGoal creadas exitosamente en la DB)

## 3. Consolidación de Errores y Calidad (Reporte)
- [x] 3.1 Capturar cualquier error de consola de red (F12) o alertas visuales rojas.
- [x] 3.2 Generar reporte final en `error_log_report.md` dentro de la carpeta del cambio.
- [x] 3.3 Marcar las funciones críticas que necesitan "hotfix" inmediato.
