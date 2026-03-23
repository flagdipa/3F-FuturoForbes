# Spec: UI Integrity & Reactivity

## Requirements

### Requirement: Global Alpine Store Initialization
*   Al cargar la aplicación, los almacenes globales de Alpine.js deben estar registrados antes de que cualquier componente de página realice su ciclo de vida `init()`.
*   **GIVEN** que el usuario accede a `/transacciones` o `/dashboard`.
*   **WHEN** se intenta interactuar con un elemento que use `$store.benefManager`.
*   **THEN** no deben aparecer errores de "undefined" en la consola del navegador.

### Requirement: Transaction Action Dispatchers
*   Los botones de la barra de acciones en `/transacciones` deben disparar las funciones correspondientes en el componente `transaccionesPage`.
*   **GIVEN** que existe al menos una transacción en la tabla.
*   **WHEN** el usuario hace clic en el botón "Nueva Transacción".
*   **THEN** se debe abrir el modal de edición de transacciones con el estado `id: 'NEW'`.

## User Scenarios

### Scenario: Create New Transaction
- **GIVEN** que la página `/transacciones` ha cargado correctamente.
- **WHEN** el usuario hace clic en el botón "Nueva Transacción" (ID `btn-new-tx`).
- **THEN** el sistema debe abrir el modal `modalNuevo` y resetear el objeto reactivo `editTx`.
