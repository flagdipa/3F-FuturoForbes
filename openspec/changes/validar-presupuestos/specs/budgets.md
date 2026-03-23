# Specs: Validar Presupuestos (Budgets)

## BDD Requirements

### Requirement: Crear presupuesto
- **GIVEN** un usuario autenticado
- **WHEN** el usuario hace click en "Nuevo Presupuesto" y llena el nombre, periodo (mensual/anual/fechas fijas) y asigna montos límite a múltiples categorías validando no sobrepasar el total (opcional).
- **THEN** un registro del modelo V2 `Budget` se crea exitosamente asociando sus `BudgetLine` hijas en el backend `/api/v1/budgets`.

### Requirement: Visualizar barra límite (Gasto Actual vs Límite Categoría)
- **GIVEN** que existe un Presupuesto de $100 en categoría `Automóvil`
- **WHEN** el usuario ingresa a la lista principal de visualización de presupuestos.
- **THEN** se devuelven además las sumas consumidas por transferencias/egresos asociados a la categoría `Automóvil` limitados por el rango de fecha.
- **AND THEN** la UI muestra la barra de progreso utilizando clases de bootsrap/UI: Normal (info/primary), Advertencia 80%+ (warning), Excedido 100%+ (danger).

### Requirement: Editar o Eliminar Presupuesto
- **GIVEN** una vista de lista de presupuestos con presupuestos activos
- **WHEN** el usuario altera los límites vía `PUT /api/v1/budgets/{id}` o borra el presupuesto completamente vía `DELETE`.
- **THEN** las transacciones previas NO se borran (mantienen su autonomía), pero la línea de control desaparece del panel.
