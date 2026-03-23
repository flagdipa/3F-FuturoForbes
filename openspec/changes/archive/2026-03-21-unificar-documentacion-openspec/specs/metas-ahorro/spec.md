## ADDED Requirements

### Requirement: Definición de metas con monto objetivo y fecha límite
El sistema SHALL permitir definir metas de ahorro con monto objetivo, fecha límite, nombre descriptivo, color e icono.

#### Scenario: Crear meta de ahorro
- **WHEN** un usuario crea una meta con target_amount y target_date
- **THEN** el sistema SHALL crear la meta con current_amount=0
- **AND** SHALL permitir asignar color e icono personalizados
- **AND** SHALL calcular progreso inicial (0%)

#### Scenario: Establecer fecha límite de meta
- **WHEN** un usuario define target_date para una meta
- **THEN** el sistema SHALL validar que la fecha sea futura
- **AND** SHALL calcular días restantes hasta la meta
- **AND** SHALL mostrar alerta si la fecha es inminente

### Requirement: Seguimiento de progreso visual
El sistema SHALL mostrar el progreso de cada meta visualmente con porcentaje completado y cantidad acumulada.

#### Scenario: Calcular progreso de meta
- **WHEN** se actualiza el current_amount de una meta
- **THEN** el sistema SHALL calcular porcentaje = (current_amount / target_amount) * 100
- **AND** SHALL actualizar visualización del progreso
- **AND** SHALL mostrar monto acumulado vs objetivo

#### Scenario: Visualizar progreso en dashboard
- **WHEN** un usuario ve sus metas en el dashboard
- **THEN** el sistema SHALL mostrar tarjetas con progreso visual
- **AND** SHALL usar barras de progreso con color de la meta
- **AND** SHALL mostrar icono asignado a la meta

### Requirement: Aportaciones a metas
El sistema SHALL permitir registrar aportaciones a las metas desde transacciones o de forma manual.

#### Scenario: Aportar a meta desde transacción
- **WHEN** una transacción de ingreso se marca como aportación a meta
- **THEN** el sistema SHALL incrementar current_amount de la meta
- **AND** SHALL vincular la transacción a la meta
- **AND** SHALL actualizar progreso visual

#### Scenario: Aportar manualmente a meta
- **WHEN** un usuario hace POST a /goals/{id}/contribute con monto
- **THEN** el sistema SHALL incrementar current_amount
- **AND** SHALL registrar la aportación con timestamp
- **AND** SHALL permitir agregar nota descriptiva

#### Scenario: Historial de aportaciones
- **WHEN** un usuario consulta una meta
- **THEN** el sistema SHALL mostrar historial de aportaciones
- **AND** SHALL incluir fecha, monto y nota de cada aportación
- **AND** SHALL permitir ordenar por fecha

### Requirement: Notificaciones al alcanzar metas
El sistema SHALL enviar notificaciones cuando se alcanza una meta, disparando hook goal_reached.

#### Scenario: Detectar meta alcanzada
- **WHEN** current_amount >= target_amount
- **THEN** el sistema SHALL marcar meta como alcanzada
- **AND** SHALL disparar hook goal_reached
- **AND** SHALL enviar notificación de felicitación

#### Scenario: Notificar exceso de meta
- **WHEN** current_amount > target_amount
- **THEN** el sistema SHALL mostrar mensaje de exceso
- **AND** SHALL calcular monto excedente
- **AND** SHALL sugerir crear nueva meta o redistribuir

### Requirement: Múltiples metas paralelas
El sistema SHALL soportar múltiples metas activas simultáneamente.

#### Scenario: Crear metas múltiples
- **WHEN** un usuario crea varias metas
- **THEN** el sistema SHALL permitir tener todas activas
- **AND** SHALL mostrar progreso de cada una independientemente
- **AND** SHALL permitir priorizar metas

#### Scenario: Ver resumen de todas las metas
- **WHEN** un usuario accede a /goals
- **THEN** el sistema SHALL listar todas las metas activas
- **AND** SHALL mostrar progreso de cada una
- **AND** SHALL permitir ordenar por fecha, monto, progreso
