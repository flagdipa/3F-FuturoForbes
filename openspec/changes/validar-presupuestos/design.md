# Design: Validar Presupuestos (Budgets)

## Context
El sistema 3F (Futuro Forbes) acaba de migrar su core a Pydantic V2 y SQLModel (models_v2.py), y estandarizado la UI hacia un estilo HUD Neon con Alpine.js (`$store`). En `estado_proyecto.md` se refleja que los presupuestos están "sin validar en V2". Es imperativo conectar el modelo actual `Budget` y `BudgetLine` en el backend con una UI frontend en `frontend/templates/budgets.html` o `frontend/templates/budgets/index.html` que sea coherente y que use la interfaz de `/api/v1/budgets` para mostrar las barras de consumo según los gastos reales de esas categorías. 

## Goals / Non-Goals
### Goals
- Integrar la vista de Presupuestos (`budgets.html`) alineada a la UI "Neon HUD" y las claves de internacionalización `$store.lang`.
- Soportar CRUD (Crear, Editar, Borrar) de un `Budget` y sus `BudgetLine` (las submetas por categoría).
- Completar y validar los endpoints REST en FastAPI `/api/budgets` que listen los presupuestos de un usuario con su _progreso o gasto actual_.
- Agregar una barra de progreso que cambie de color a `warning` al 80% y a `danger` al >100% gastado del monto presupuestado.

### Non-Goals
- No se implementarán notificaciones Push ni emails automáticos de budget excedido en esta fase. Se validarán únicamente a nivel UI visual/dashboard.
- No se creará la lógica para auto-reasignar sobrantes de un mes a otro (presupuestos rollover), solo presupuestos fijos por fecha (start, end date).

## Technical Approach
1. **Backend Integration (API)**:
    - Revisar `backend/api/v1/budgets.py` o crear el router V2 si no existe. 
    - El GET de budgets devolverá el `Budget` V2, parseando en las líneas de detalle (`BudgetLine`) la sumatoria de las **Transacciones V2** que caigan en la categoría de cada línea, durante el periodo `start_date` a `end_date` del Presupuesto.
    - Endpoints requeridos: `GET /api/budgets/`, `POST /api/budgets/`, `PUT /api/budgets/{id}`, `DELETE /api/budgets/{id}`.

2. **Frontend UI (`budgets.html`)**:
    - Crear o modificar un manejador con Alpine `x-data="budgetManager"`, emulando el comportamiento estable de `transactions` y `goals`.
    - Realizar peticiones a `/api/budgets/` consumiéndolos con Axios/Fetch y el JWT actual.
    - Cargar `collections.categories` globalmente para que el usuario pueda agregar `BudgetLine` con selector de la categoría.

3. **Gasto dinámico / Progress calculation**:
    - Idealmente, el backend emite el JSON con `amount_spent` calculado. 
    - En el frontend: `porcentaje_consumido = (amount_spent / amount) * 100`. 
    - Estilos bootstrap nativos en Progress bar `<div class="progress-bar bg-success" :style="'width: ' + percent + '%'"></div>`.

## Risks / Trade-offs
- Si la suma de gastos se calcula "al vuelo" (on-the-fly request), el listado inicial de presupuestos podría hacer la carga ligeramente más pesada si hay muchas transacciones. Puesto que no iteramos en bases de datos a escala de millones aún, este `trade-off` "on-the-fly" en SQLite es seguro por ahora versus la complicación de almacenar saldos cacheados en tabla para cada inserción de transacción u OCR trigger.
