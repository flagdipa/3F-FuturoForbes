## Why

El sistema tiene una dependencia crítica en modelos V1 legacy que impide la limpieza completa. El archivo `backend/api/retro.py` importa y usa `TipoEntidadFinanciera` e `IdentidadFinanciera` desde `models.py`, manteniendo código legacy activo en producción.

**Problema:** La limpieza de archivos V1 no puede proceder hasta que esta funcionalidad sea migrada a los modelos V2 (`Institution`).

**Impacto:**
- Bloquea la limpieza completa del codebase
- Mantiene archivos legacy innecesarios
- Genera confusión sobre qué código está activo
- Impide el mantenimiento profesional del sistema

## What Changes

Migrar completamente la funcionalidad de entidades financieras del sistema legacy V1 al modelo V2 unificado:

### Migración de Datos
- **TipoEntidadFinanciera** → **Institution.type** (mapeo de tipos)
- **IdentidadFinanciera** → **Institution** (conversión completa)

### Migración de Código
- Reemplazar imports de `models.py` por imports de `models_v2.py`
- Actualizar `backend/api/retro.py` para usar `Institution` en lugar de modelos legacy
- Eliminar referencias a `TipoEntidadFinanciera` e `IdentidadFinanciera`
- Actualizar `backend/models/__init__.py` para remover imports legacy

### Migración de Base de Datos
- Script de migración de datos de tablas legacy a tablas V2
- Preservar relaciones y datos existentes
- Eliminar tablas legacy después de migración exitosa

## Capabilities

### Modified Capabilities
- `financial-entities-api`: Migrar endpoints legacy a usar modelos V2
- `database-models`: Eliminar dependencias de modelos V1

### New Capabilities
- `data-migration-tool`: Herramienta para migrar datos entre esquemas

## Impact

- **Backend:** Migración completa de API retro a modelos V2
- **Base de Datos:** Migración de datos y eliminación de tablas legacy
- **Frontend:** Sin impacto (usa endpoints existentes)
- **Cleanup:** Habilita eliminación completa de archivos V1
- **Tests:** Actualización de tests para usar modelos V2