## ADDED Requirements

### Requirement: Gestión de múltiples tipos de cuentas
El sistema SHALL permitir a los usuarios crear y gestionar cuentas de diferentes tipos con soporte multi-moneda y saldos en tiempo real.

#### Scenario: Crear cuenta bancaria
- **WHEN** un usuario autenticado envía una solicitud POST a /api/v1/accounts con datos válidos
- **THEN** el sistema SHALL crear una nueva cuenta asociada al usuario con saldo inicial especificado
- **AND** SHALL retornar el ID de la cuenta creada

#### Scenario: Listar cuentas del usuario
- **WHEN** un usuario autenticado solicita GET /api/v1/accounts
- **THEN** el sistema SHALL retornar todas las cuentas activas del usuario con sus saldos actuales
- **AND** SHALL incluir información de moneda para cada cuenta

#### Scenario: Actualizar saldo de cuenta
- **WHEN** se crea, actualiza o elimina una transacción asociada a una cuenta
- **THEN** el sistema SHALL recalcular automáticamente el saldo actual de la cuenta
- **AND** SHALL registrar el cambio en el historial de saldos

#### Scenario: Soporte multi-moneda en cuentas
- **WHEN** un usuario crea una cuenta con código de moneda diferente a la moneda base
- **THEN** el sistema SHALL permitir operaciones en esa moneda
- **AND** SHALL almacenar la moneda junto con todas las transacciones de esa cuenta

### Requirement: Registro de transacciones con doble entrada
El sistema SHALL implementar contabilidad de doble entrada donde cada transacción afecta al menos dos cuentas (débito y crédito), garantizando la integridad financiera.

#### Scenario: Crear transacción de gasto
- **WHEN** un usuario crea una transacción de tipo EXPENSE
- **THEN** el sistema SHALL decrementar el saldo de la cuenta origen
- **AND** SHALL crear registros de débito y crédito balanceados
- **AND** SHALL aplicar la categoría y beneficiario especificados

#### Scenario: Crear transacción de ingreso
- **WHEN** un usuario crea una transacción de tipo INCOME
- **THEN** el sistema SHALL incrementar el saldo de la cuenta destino
- **AND** SHALL crear registros de débito y crédito balanceados

#### Scenario: Crear transferencia entre cuentas
- **WHEN** un usuario crea una transacción de tipo TRANSFER entre dos cuentas
- **THEN** el sistema SHALL decrementar el saldo de la cuenta origen
- **AND** SHALL incrementar el saldo de la cuenta destino
- **AND** SHALL aplicar conversión de moneda si las cuentas tienen divisas diferentes

#### Scenario: Dividir transacción en múltiples categorías
- **WHEN** un usuario crea una transacción con splits (divisiones)
- **THEN** el sistema SHALL permitir asignar montos parciales a diferentes categorías
- **AND** SHALL validar que la suma de los splits sea igual al monto total
- **AND** SHALL crear registros separados para cada split

### Requirement: Estados de conciliación
El sistema SHALL permitir marcar transacciones como reconciliadas o pendientes para facilitar la conciliación bancaria.

#### Scenario: Marcar transacción como reconciliada
- **WHEN** un usuario actualiza el estado de una transacción a RECONCILED
- **THEN** el sistema SHALL persistir el estado reconciliado
- **AND** SHALL permitir filtrar transacciones por estado en reportes

#### Scenario: Conciliación de cuenta completa
- **WHEN** un usuario ejecuta la conciliación de una cuenta con fecha de corte
- **THEN** el sistema SHALL marcar todas las transacciones hasta esa fecha como reconciliadas
- **AND** SHALL calcular y mostrar el balance reconciliado

#### Scenario: Filtrar transacciones no reconciliadas
- **WHEN** un usuario solicita ver transacciones pendientes de conciliación
- **THEN** el sistema SHALL retornar solo transacciones con estado PENDING
- **AND** SHALL permitir seleccionar múltiples transacciones para conciliación masiva

### Requirement: Sistema jerárquico de categorías
El sistema SHALL proporcionar categorías y subcategorías organizadas jerárquicamente con colores e iconos para identificación visual.

#### Scenario: Crear categoría principal
- **WHEN** un usuario crea una categoría sin parent_id
- **THEN** el sistema SHALL crear una categoría de nivel superior
- **AND** SHALL permitir asignar color e icono personalizados

#### Scenario: Crear subcategoría
- **WHEN** un usuario crea una categoría con parent_id especificado
- **THEN** el sistema SHALL crear una subcategoría bajo la categoría padre
- **AND** SHALL validar que la categoría padre exista y sea del mismo tipo

#### Scenario: Listar categorías en estructura de árbol
- **WHEN** un usuario solicita el listado de categorías
- **THEN** el sistema SHALL retornar las categorías en estructura jerárquica
- **AND** SHALL incluir conteo de transacciones por categoría

### Requirement: Gestión de beneficiarios con auto-categorización
El sistema SHALL permitir gestionar beneficiarios (payees) y configurar reglas de auto-categorización basadas en ellos.

#### Scenario: Crear beneficiario con categoría por defecto
- **WHEN** un usuario crea un beneficiario con default_category_id
- **THEN** el sistema SHALL asociar la categoría por defecto al beneficiario
- **AND** SHALL aplicar automáticamente esa categoría en transacciones futuras con ese beneficiario

#### Scenario: Auto-categorización de transacción
- **WHEN** el sistema detecta una transacción con beneficiario existente
- **THEN** el sistema SHALL sugerir la categoría por defecto del beneficiario
- **AND** SHALL permitir al usuario aceptar o modificar la categoría sugerida

#### Scenario: Buscar beneficiarios
- **WHEN** un usuario busca beneficiarios por nombre
- **THEN** el sistema SHALL retornar beneficiarios que coincidan parcial o totalmente
- **AND** SHALL incluir historial de transacciones por beneficiario

### Requirement: Precisión decimal en montos
El sistema SHALL utilizar tipos de datos Decimal con precisión exacta para todos los montos financieros, prohibiendo el uso de float.

#### Scenario: Almacenar monto con decimales
- **WHEN** el sistema almacena un monto con 2 decimales (ej: $100.50)
- **THEN** el sistema SHALL usar Decimal(10, 2) para garantizar precisión
- **AND** SHALL evitar errores de redondeo propios de float

#### Scenario: Realizar cálculos con múltiples divisas
- **WHEN** el sistema convierte montos entre diferentes divisas
- **THEN** el sistema SHALL usar precisión Decimal para todas las operaciones
- **AND** SHALL redondear al final según las reglas de la moneda destino

### Requirement: Soft delete de datos financieros
El sistema SHALL implementar soft delete para todas las entidades financieras, nunca eliminando físicamente los datos.

#### Scenario: Eliminar cuenta
- **WHEN** un usuario solicita eliminar una cuenta
- **THEN** el sistema SHALL marcar la cuenta como eliminada (deleted_at timestamp)
- **AND** SHALL mantener todas las transacciones asociadas
- **AND** SHALL ocultar la cuenta de listados normales

#### Scenario: Eliminar transacción
- **WHEN** un usuario solicita eliminar una transacción
- **THEN** el sistema SHALL marcar la transacción como eliminada
- **AND** SHALL revertir los cambios de saldo en las cuentas afectadas
- **AND** SHALL mantener el registro para auditoría

#### Scenario: Recuperar datos eliminados
- **WHEN** un administrador solicita ver datos eliminados
- **THEN** el sistema SHALL mostrar entidades marcadas como eliminadas
- **AND** SHALL permitir restaurarlas si es necesario

### Requirement: Etiquetado flexible de transacciones
El sistema SHALL permitir asignar múltiples etiquetas (tags) a cada transacción para clasificación flexible.

#### Scenario: Asignar etiquetas a transacción
- **WHEN** un usuario crea o actualiza una transacción con tags
- **THEN** el sistema SHALL asociar las etiquetas a la transacción
- **AND** SHALL permitir búsqueda y filtrado por etiquetas

#### Scenario: Filtrar transacciones por etiqueta
- **WHEN** un usuario solicita transacciones filtradas por etiqueta específica
- **THEN** el sistema SHALL retornar solo transacciones con esa etiqueta
- **AND** SHALL permitir filtrar por múltiples etiquetas (AND/OR)

#### Scenario: Reporte por etiquetas
- **WHEN** un usuario genera un reporte agrupado por etiquetas
- **THEN** el sistema SHALL mostrar totales y distribución por etiqueta
- **AND** SHALL permitir comparar períodos
