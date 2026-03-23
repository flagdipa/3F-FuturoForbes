# Tasks: Validar Presupuestos (Budgets)

## 1. Backend API Review
- [x] 1.1 Verificar el CRUD en `backend/api/v1/budgets/router.py` para asegurar que está funcionando en conjunto con Pydantic V2 (`BudgetCreate`, `BudgetUpdate`).
- [x] 1.2 Revisar o implementar en el `GET /api/v1/budgets/` el cálculo del total gastado (`amount_spent`) para cada línea del presupuesto (`BudgetLine`) sumando las transacciones correspondientes en `start_date` a `end_date`.

## 2. Frontend Layout & Alpine.js
- [x] 2.1 Reestructurar `frontend/templates/budgets.html` o `frontend/templates/budgets/index.html` para usar diseño Neon HUD (clases `neon-card`, `text-primary`, backgrounds).
- [x] 2.2 Crear el script Alpine.js `budgetManager` en `frontend/static/js/` (o inline) con soporte para listar la colección y tener métodos `loadCollections`, `newBudget()`, `editBudget()`, `deleteBudget()`.
- [x] 2.3 Incluir y traducir a `$store.lang` todas las etiquetas principales del módulo Presupuestos (`budgets.title`, `common.new`, `common.delete`).

## 3. UI Componentes: Progress Bar
- [x] 3.1 Dentro de la carga de presupuestos interactiva, calcular el porcentaje dinámico de gasto por cada línea: `(spent / amount_limit) * 100`.
- [x] 3.2 Visualizar para cada `BudgetLine` un badge/barra progresiva.
- [x] 3.3 Validar que el color varíe: success/info (<80%), warning (80-99%), danger (>=100%).

## 4. UI Componentes: Formulario modal
- [x] 4.1 Crear modal `modalNuevoPresupuesto` para ingresar Meta general, `start_date`, `end_date`.
- [x] 4.2 Dentro del modal, incluir opción dinámica de "Agregar Línea" de gasto y poder atarla a una Categoría (`select` desde `collections.categories`).

## 5. End-to-End Validation
- [x] 5.1 Crear presupuesto para este mes con tope $50,000 en Categoría "Comida".
- [x] 5.2 Registrar transacción ficticia de $45,000 en Categoría "Comida" desde `transactions.html`.
- [x] 5.3 Volver al módulo de presupuestos y validar que la barra se ponga amarilla (90%).
- [x] 5.4 Actualizar `estado_proyecto.md` y mover "Validar Presupuestos" de ALTA a COMPLETADA.
