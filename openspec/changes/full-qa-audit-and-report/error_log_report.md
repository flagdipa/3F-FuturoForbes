# Reporte de Errores: Auditoría General Post-Refactor V2

Este reporte detalla las inconsistencias y fallas críticas detectadas durante la navegación con el Browser Agent en un entorno local (`uvicorn`).

## 🔴 Prioridad ALTA (Bloqueantes / Funcionales)

### 1. Fallo Crítico en Endpoint de Presupuestos (500 Error)
- **Módulo**: Presupuestos (Budgets).
- **Endpoint**: `GET /api/v1/budgets/`.
- **Descripción**: La página carga la estructura, pero el listado de presupuestos falla con un error 500. Esto impide ver o editar presupuestos existentes.
- **Posible Causa**: Discrepancia en el modelo de respuesta esperado vs el retornado por el router tras la actualización de `models_v2.py`.

### 2. Fallo de Carga en Módulo de Metas (500 Error + UX)
- **Módulo**: Metas (Saving Goals).
- **Endpoint**: `GET /api/v1/goals/`.
- **Descripción**: La vista se queda en estado de carga ("Cargando metas...") infinitamente debido a un error 500 en la API. Además, el título principal muestra `goals.title` (i18n roto).

### 3. Errores de Alpine JS en Transacciones (Edit/OCR)
- **Módulo**: Transacciones.
- **Descripción**: Al intentar interactuar con modales, la consola reporta `Alpine Expression Error: editTx is not defined`.
- **Impacto**: Impide la edición de transacciones existentes desde la tabla.

## 🟡 Prioridad MEDIA (i18n / Estética)

### 4. Claves de Traducción no Resueltas (Sidebar)
- **Módulo**: Navegación General.
- **Descripción**: Varios ítems del menú lateral no resuelven su traducción:
  - `nav.scheduled`
  - `nav.vault`
  - `nav.plugins`
- **Contexto**: Probablemente falten estas claves en los archivos JSON de locales o `i18n.js` no los está cargando.

### 5. Indicadores de Sistema Estáticos
- **Módulo**: Configuración (Settings).
- **Descripción**: Los indicadores de "Estado de DB" y "Salud del Sistema" se quedan en "Cargando..." permanentemente.

## 🔵 Prioridad BAJA (Detalles Menores)

### 6. Nombre de Usuario Hardcodeado
- **Ubicación**: Header / Dashboard.
- **Descripción**: Muestra "Fer21gon" a pesar de haber logueado con `qa_test_unique@example.com`.
- **Causa**: Valor estático en el HTML del Dashboard.

---
**Próximos Pasos**: Proponer un cambio incremental para corregir los errores 500 en Budgets/Goals y actualizar el sistema de i18n.
