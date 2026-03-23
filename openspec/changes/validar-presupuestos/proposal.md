# Proposal: Validar Presupuestos (Budgets)

## Problem Context
El sistema 3F (Futuro Forbes) cuenta con el modelo de datos `Budget` y `BudgetLine` en el backend V2 (`models_v2.py`) para permitir a los usuarios crear, editar y hacer seguimiento de sus metas de gasto por categorías. Sin embargo, según el documento `estado_proyecto.md`, esta funcionalidad todavía se encuentra sin validar en producción. La UI actual necesita conectarse a los nuevos endpoints, asegurar la integridad del guardado de presupuestos y sus líneas de detalle, y habilitar visualmente las alertas y seguimientos de consumo versus el gasto real (calculado desde transacciones V2).

## Proposed Solution
Se propone validar, unificar e implementar end-to-end el módulo de presupuestos (Budgets). Esto incluye:
1. Confirmar/crear los endpoints REST `/api/v1/budgets` para soportar V2 y operaciones CRUD limpias sobre `Budget` y `BudgetLine`.
2. Actualizar el frontend (`frontend/templates/budgets/index.html` o equivalente) para que coincida con las convenciones Neon HUD e idioma inglés/multi-lenguaje (`$store.lang`).
3. Calcular en tiempo real el progreso de consumo de cada línea de presupuesto leyendo del módulo unificado de `Transactions`, y mostrar barras de progreso y alertas (colores warning/danger al sobrepasar umbrales) en el frontend.

## Impact
- **Backend API**: Endpoints de `/budgets` (creación, edición, borrado, listado y cálculo de progreso).
- **Frontend UI**: Formularios de presupuestos, lista principal de presupuestos, modales de líneas de presupuesto, validaciones de frontend.
- **Data Model**: `models_v2.Budget` y `models_v2.BudgetLine` garantizan relaciones con los usuarios y categorías.
- No hay migración destructiva, es principalmente completar la integración frontend-backend, testear flujo, y visualizaciones.
