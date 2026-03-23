## ADDED Requirements

### Requirement: Configuración de frecuencias flexibles
El sistema SHALL soportar frecuencias: diaria, semanal, mensual, anual y personalizada.

#### Scenario: Crear transacción mensual
- **WHEN** un usuario configura frequency=MONTHLY con interval=1
- **THEN** el sistema SHALL programar ejecución cada mes
- **AND** SHALL calcular next_execution_date automáticamente

#### Scenario: Crear transacción semanal
- **WHEN** un usuario configura frequency=WEEKLY
- **THEN** el sistema SHALL programar ejecución cada 7 días
- **AND** SHALL permitir seleccionar día de la semana

#### Scenario: Crear transacción con intervalo personalizado
- **WHEN** un usuario configura frequency=CUSTOM con interval=15
- **THEN** el sistema SHALL ejecutar cada 15 días
- **AND** SHALL calcular próximas fechas basado en el intervalo

### Requirement: Auto-ejecución con confirmación opcional
El sistema SHALL permitir configurar si la transacción se ejecuta automáticamente o requiere confirmación.

#### Scenario: Configurar auto-ejecución
- **WHEN** un usuario establece auto_execute=true
- **THEN** el sistema SHALL crear transacción automáticamente en next_execution_date
- **AND** SHALL NOT requerir confirmación del usuario

#### Scenario: Configurar con confirmación
- **WHEN** un usuario establece auto_execute=false
- **THEN** el sistema SHALL notificar al usuario cuando toca ejecutar
- **AND** SHALL esperar confirmación antes de crear transacción
- **AND** SHALL permitir editar detalles antes de confirmar

### Requirement: Notificaciones de recordatorio
El sistema SHALL enviar recordatorios antes de la ejecución de transacciones programadas.

#### Scenario: Enviar recordatorio previo
- **WHEN** se acerca fecha de ejecución (configurable: 1-7 días antes)
- **THEN** el sistema SHALL enviar notificación de recordatorio
- **AND** SHALL incluir detalles de la transacción programada

#### Scenario: Recordatorio de transacción pendiente
- **WHEN** pasa la fecha de ejecución sin confirmar
- **THEN** el sistema SHALL enviar recordatorio de urgencia
- **AND** SHALL permitir ejecutar, saltar o posponer

### Requirement: Excepciones y fechas a saltar
El sistema SHALL permitir definir excepciones para saltar fechas específicas.

#### Scenario: Agregar excepción
- **WHEN** un usuario agrega fecha a lista de excepciones
- **THEN** el sistema SHALL saltar esa fecha en cálculo de próximas ejecuciones
- **AND** SHALL recalcular next_execution_date

#### Scenario: Saltar ejecución manualmente
- **WHEN** un usuario ejecuta POST /recurring/{id}/skip
- **THEN** el sistema SHALL agregar fecha actual como excepción
- **AND** SHALL recalcular próxima ejecución
- **AND** SHALL NOT crear transacción para esta fecha

### Requirement: Ejecución manual
El sistema SHALL permitir ejecutar una transacción recurrente manualmente en cualquier momento.

#### Scenario: Ejecutar ahora
- **WHEN** un usuario hace POST /recurring/{id}/execute
- **THEN** el sistema SHALL crear transacción inmediatamente
- **AND** SHALL usar los datos configurados
- **AND** SHALL recalcular next_execution_date normal
