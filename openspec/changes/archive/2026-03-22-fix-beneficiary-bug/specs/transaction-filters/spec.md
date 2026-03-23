## ADDED Requirements

### Requirement: Filtrado de transacciones por beneficiario
El sistema SHALL permitir filtrar transacciones por beneficiario en la lista de transacciones.

#### Scenario: Filtrar transacciones por beneficiario específico
- **WHEN** el usuario selecciona un beneficiario en el filtro de transacciones
- **THEN** el sistema muestra solo las transacciones donde payee_id coincide con el beneficiario seleccionado
- **AND** las transacciones se ordenan por fecha descendente

#### Scenario: Limpiar filtro de beneficiario
- **WHEN** el usuario limpia el filtro de beneficiario
- **THEN** el sistema muestra todas las transacciones sin filtro por beneficiario
- **AND** mantiene otros filtros activos (fecha, categoría, etc.)

### Requirement: Visualización de transacciones del beneficiario
El sistema SHALL mostrar las transacciones asociadas a un beneficiario desde la vista de gestión de beneficiarios.

#### Scenario: Ver transacciones desde modal de beneficiario
- **WHEN** el usuario hace clic en "Ver transacciones" de un beneficiario en el modal de gestión
- **THEN** el sistema carga las últimas 50 transacciones del beneficiario
- **AND** muestra fecha, monto, descripción y estado de conciliación
- **AND** indica si el beneficiario tiene transacciones asociadas

#### Scenario: Beneficiario sin transacciones
- **WHEN** el usuario intenta ver transacciones de un beneficiario sin movimientos
- **THEN** el sistema muestra mensaje "No hay transacciones asociadas"
- **AND** permite eliminar el beneficiario desde el modal

## MODIFIED Requirements

(No hay requisitos existentes que modifiquen comportamiento - estos son validaciones adicionales)
