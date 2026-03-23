## MODIFIED Requirements

### Requirement: API de entidades financieras usa modelos V2
El endpoint `/financial-entities/*` debe usar exclusivamente modelos V2 (`Institution`) en lugar de modelos legacy V1 (`TipoEntidadFinanciera`, `IdentidadFinanciera`).

#### Scenario: Imports actualizados en retro.py
- **WHEN** se revisa el archivo `backend/api/retro.py`
- **THEN** debe importar `Institution` desde `models_v2`
- **AND** NO debe importar `TipoEntidadFinanciera` ni `IdentidadFinanciera` desde `models`
- **AND** debe eliminar las clases `RetroTipoEntidadIn` y `RetroEntidadIn`

#### Scenario: Endpoints actualizados
- **WHEN** se revisan los endpoints `/financial-entities/types` y `/financial-entities/institutions`
- **THEN** deben usar `Institution` en lugar de `TipoEntidadFinanciera`/`IdentidadFinanciera`
- **AND** deben mantener la misma interfaz API para compatibilidad con frontend
- **AND** deben mapear campos legacy a campos V2:
  - `nombre_tipo` → `type`
  - `icono` → `icon`
  - `color` → (integrar en `name` o campo adicional)
  - `activo` → `deleted_at is None` (usar soft delete)

#### Scenario: Seed actualizado
- **WHEN** se ejecuta el endpoint `/financial-entities/seed`
- **THEN** debe crear registros `Institution` en lugar de `TipoEntidadFinanciera`
- **AND** debe usar el formato V2 para los datos

### Requirement: Eliminación de dependencias legacy
El sistema no debe tener dependencias activas a modelos V1 legacy.

#### Scenario: Imports legacy eliminados
- **WHEN** se revisa `backend/models/__init__.py`
- **THEN** debe eliminar `from .models import TipoEntidadFinanciera, IdentidadFinanciera`
- **AND** debe eliminar estas clases de `metadata_models`
- **AND** todos los imports deben apuntar a `models_v2`

#### Scenario: No más referencias a modelos V1
- **WHEN** se busca en todo el código `TipoEntidadFinanciera` e `IdentidadFinanciera`
- **THEN** no debe encontrar resultados (excepto posiblemente en comentarios)

## ADDED Requirements

### Requirement: Mapeo de campos legacy a V2
El sistema debe proporcionar un mapeo claro de campos entre modelos legacy y V2.

#### Scenario: Campos mapeados correctamente
- **WHEN** se crea una nueva entidad financiera
- **THEN** los campos deben mapearse:
  - Legacy: `nombre_tipo`, `icono`, `color`, `activo`
  - V2: `type`, `icon`, (color integrado), `deleted_at is None`
  - Legacy: `nombre`, `sucursal`, `direccion`, `web`, `contacto`, `telefono`, `cuit`
  - V2: `name`, `branch`, `address`, `website`, `contact`, `phone`, `cuit`

#### Scenario: Compatibilidad con frontend
- **WHEN** el frontend consume los endpoints
- **THEN** debe recibir la misma estructura de datos
- **AND** no debe notar diferencia en la API