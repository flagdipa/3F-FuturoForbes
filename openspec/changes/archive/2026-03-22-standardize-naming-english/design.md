# Design: Standardization of Variable Naming to English

## Architecture Overview
This change affects the entire system stack, starting from the database models through the API layer to the Alpine.js state stores and HTML templates.

## Data Model Updates (models_v2.py)
Update the following models to use English field names:

### Category Model
- `id_categoria` -> `id` (Inherited from SQLModel's default or explicitly defined)
- `nombre_categoria` -> `name`
- `id_padre` / `id_categoria_padre` -> `parent_id`
- `notas` -> `notes`

### Account Model (To be confirmed if not already English)
- `id_cuenta` -> `id`
- `nombre_cuenta` -> `name`
- `tipo_cuenta` -> `account_type`
- `saldo_inicial` -> `initial_balance`
- `moneda` -> `currency`

### Transaction Model (To be confirmed)
- `monto` -> `amount`
- `fecha` -> `date`
- `descripcion` -> `description`
- `estado` -> `status`

## API Layer Updates
Update Pydantic schemas in `backend/api/v1/*.py` to reflect the new English field names.
- Ensure that JSON responses use the new field names.
- Update endpoint parameters (e.g., `/categorias/{id_categoria}` -> `/categories/{id}`).

## Frontend State Management (Alpine.js Stores)
Update the following stores:
- `catForm`: `id_categoria` -> `id`, `nombre_categoria` -> `name`, `id_padre` -> `parent_id`, `notas` -> `notes`.
- `mergeData`: `id_origen` -> `source_id`, `id_destino` -> `target_id`, `eliminar_origen` -> `delete_source`.
- `benefForm`: Already partially English, ensure full consistency.

## Frontend Templates (HTML)
Perform a global find-and-replace for the renamed variables across all `.html` files in `frontend/templates/`. This includes:
- `x-model` bindings.
- `x-text` and `${...}` expressions.
- Event listeners (`@click`, etc.).

## Backward Compatibility
- For a smooth transition, the backend can temporarily support both names during the migration phase, but the final goal is complete removal of Spanish names.
- (Recommended) Perform the rename in one go to avoid "orphan" fields.
