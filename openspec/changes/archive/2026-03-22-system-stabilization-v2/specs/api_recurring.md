# Spec: API Recurring Implementation

## Requirements

### Requirement: Recurring Transactions Endpoint
*   El backend debe exponer una ruta `/api/v1/recurring/` consistente con el esquema de SQLModel V2.
*   **GIVEN** que el servidor FastAPI está operativo.
*   **WHEN** se solicita el listado de recurrencias vía `GET`.
*   **THEN** el sistema debe devolver un JSON con la estructura: `{"data": [...], "status": "success"}`.

### Requirement: Recurring Model Relationship
*   Toda transacción recurrente debe estar asociada a una cuenta (`account_id`), una categoría (`category_id`) y opcionalmente a un beneficiario (`payee_id`).

## API Scenarios

### Scenario: List Recurring Tasks
- **GIVEN** que existen tareas recurrentes en la base de datos `SQLModel`.
- **WHEN** el frontend dispara `api.get('/recurring/')`.
- **THEN** la respuesta debe contener los campos `frequency`, `interval`, `start_date` y `next_date` formateados en ISO.
