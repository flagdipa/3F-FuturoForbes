# Tasks: Estabilización Final V2 y Cleanup

## 1. Mantenimiento de Base de Datos
- [x] 1.1 Eliminar el archivo `3f_app.db` localmente (o forzar el recreado de tablas).
- [x] 1.2 Ejecutar `backend/main.py` para disparar `init_db()` y recrear todas las tablas con los campos `created_at` del modelo V2.
- [x] 1.3 Verificar que el endpoint `GET /api/v1/goals/` responde `[]` (200 OK) para un usuario nuevo, en lugar de 500.

## 2. Correcciones de i18n y Layout (Frontend)
- [x] 2.1 Reemplazar "Fer21gon" con el nombre del usuario real (dinámico) en `frontend/templates/dashboard.html` y otros headers.
- [x] 2.2 Completar el archivo `static/locales/es.json` con las claves de navegación y módulos (`nav.scheduled`, `nav.vault`, `nav.plugins`, `nav.tags`, `goals.title`, `budgets.title`, `common.duplicate`, `settings.db_management`).
- [x] 2.3 Idem para `static/locales/en.json`.

## 3. Estabilización de JS (Alpine Errors)
- [x] 3.1 Identificar el archivo responsable de manejar el modal de transacciones y añadir la inicialización de `editTx`, `isScanningReceipt`, `saving`, `attachments`.
- [x] 3.2 Asegurarse de que el script `static/js/transactions.js` se cargue correctamente en las vistas de transacciones.
- [x] 3.3 Validar en consola (F12) que desaparecen los `Alpine Expression Error`.

## 4. Validación Integrada
- [x] 4.1 Loguearse -> Dashboard -> Metas -> Asegurar que el spinner desaparece y la vista carga (incluso si está vacía).
- [x] 4.2 Repetir en Presupuestos.
- [x] 4.3 Ver Transacciones y verificar que no hay errores de consola al cargar la tabla.
