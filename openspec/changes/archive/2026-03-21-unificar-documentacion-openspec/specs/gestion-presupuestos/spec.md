## ADDED Requirements

### Requirement: Creación de presupuestos con múltiples períodos
El sistema SHALL permitir crear presupuestos de tipo mensual, anual o rolling con fecha de inicio y fin opcional.

#### Scenario: Crear presupuesto mensual
- **WHEN** un usuario crea un presupuesto con type=MONTHLY
- **THEN** el sistema SHALL crear presupuesto válido para el mes especificado
- **AND** SHALL asociar categorías y montos al presupuesto
- **AND** SHALL calcular automáticamente fechas de inicio y fin del mes

#### Scenario: Crear presupuesto anual
- **WHEN** un usuario crea un presupuesto con type=ANNUAL
- **THEN** el sistema SHALL crear presupuesto válido para todo el año
- **AND** SHALL permitir definir presupuestos por categoría para el año completo

#### Scenario: Crear presupuesto rolling
- **WHEN** un usuario crea un presupuesto con type=ROLLING
- **THEN** el sistema SHALL crear presupuesto que se mueve continuamente
- **AND** SHALL calcular período actual basado en fecha actual

#### Scenario: Asignar categorías al presupuesto
- **WHEN** un usuario configura categorías para un presupuesto
- **THEN** el sistema SHALL crear registros BudgetCategory con monto asignado
- **AND** SHALL permitir asignar diferentes montos por categoría
- **AND** SHALL validar que el total no exceda el presupuesto general

### Requirement: Seguimiento de gasto vs presupuesto
El sistema SHALL calcular en tiempo real el gasto real vs presupuestado para cada categoría y el total.

#### Scenario: Calcular estado del presupuesto
- **WHEN** un usuario consulta el estado de un presupuesto
- **THEN** el sistema SHALL sumar todas las transacciones de gasto en el período
- **AND** SHALL agrupar gastos por categoría
- **AND** SHALL calcular porcentaje usado de cada categoría
- **AND** SHALL calcular porcentaje usado del presupuesto total

#### Scenario: Mostrar progreso visual del presupuesto
- **WHEN** se visualiza un presupuesto en la UI
- **THEN** el sistema SHALL mostrar barra de progreso con porcentaje usado
- **AND** SHALL usar colores: verde (<80%), amarillo (80-100%), rojo (>100%)
- **AND** SHALL mostrar monto presupuestado vs gastado vs restante

#### Scenario: Actualizar presupuesto automáticamente
- **WHEN** se crea, actualiza o elimina una transacción de gasto
- **THEN** el sistema SHALL recalcular automáticamente el estado del presupuesto afectado
- **AND** SHALL actualizar el porcentaje usado
- **AND** SHALL verificar si se debe disparar alerta

### Requirement: Alertas de presupuesto excedido
El sistema SHALL enviar alertas cuando el gasto excede el presupuesto de una categoría o el total, disparando hooks para notificaciones.

#### Scenario: Detectar presupuesto de categoría excedido
- **WHEN** el gasto de una categoría supera el monto presupuestado
- **THEN** el sistema SHALL marcar la categoría como excedida
- **AND** SHALL disparar hook budget_alert con percentage > 100
- **AND** SHALL registrar evento de alerta

#### Scenario: Detectar presupuesto total excedido
- **WHEN** el gasto total supera el presupuesto general
- **THEN** el sistema SHALL marcar el presupuesto como excedido
- **AND** SHALL disparar hook budget_alert
- **AND** SHALL enviar notificación al usuario

#### Scenario: Alerta preventiva al 80%
- **WHEN** el gasto alcanza el 80% del presupuesto (configurable)
- **THEN** el sistema SHALL enviar alerta preventiva
- **AND** SHALL sugerir revisar gastos restantes del período

#### Scenario: Configurar threshold de alerta
- **WHEN** un usuario configura alert_threshold para una categoría
- **THEN** el sistema SHALL usar ese porcentaje para alertas
- **AND** SHALL default a 80% si no se especifica

### Requirement: Configuración de alertas threshold
El sistema SHALL permitir configurar threshold de alerta por categoría (default: 80%).

#### Scenario: Establecer threshold personalizado
- **WHEN** un usuario define alert_threshold=90% para una categoría
- **THEN** el sistema SHALL almacenar el threshold en BudgetCategory
- **AND** SHALL usar este valor para evaluar alertas

#### Scenario: Threshold por defecto
- **WHEN** no se especifica alert_threshold para una categoría
- **THEN** el sistema SHALL usar 80% como valor por defecto
- **AND** SHALL aplicar a todas las evaluaciones de esa categoría

### Requirement: Reportes de cumplimiento de presupuesto
El sistema SHALL generar reportes comparativos mostrando presupuestado vs real vs variación.

#### Scenario: Generar reporte de presupuesto
- **WHEN** un usuario solicita reporte de presupuesto
- **THEN** el sistema SHALL mostrar tabla con todas las categorías
- **AND** SHALL incluir: presupuestado, gastado, restante, % usado
- **AND** SHALL mostrar variación (diferencia absoluta y porcentual)

#### Scenario: Exportar reporte de presupuesto
- **WHEN** un usuario exporta reporte de presupuesto
- **THEN** el sistema SHALL generar archivo en formato seleccionado
- **AND** SHALL incluir todos los datos del presupuesto
- **AND** SHALL aplicar filtros de fecha si se especifican

#### Scenario: Comparar períodos de presupuesto
- **WHEN** un usuario compara presupuestos de diferentes períodos
- **THEN** el sistema SHALL mostrar evolución del cumplimiento
- **AND** SHALL calcular tendencias (mejorando/empeorando)
