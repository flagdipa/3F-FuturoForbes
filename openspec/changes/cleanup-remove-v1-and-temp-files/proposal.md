## Why

El sistema 3F ha migrado completamente a la arquitectura V2 con modelos SQLModel unificados en `models_v2.py`. Sin embargo, existen archivos legacy de la V1 que ya no se utilizan pero siguen ocupando espacio y generando confusión. Estos archivos incluyen:

- Modelos antiguos en español que han sido reemplazados por modelos V2 en inglés
- Archivos temporales de testing y debugging
- Caché de Python (__pycache__, .pyc)
- Logs temporales del servidor

Mantener estos archivos:
1. Genera confusión sobre qué código está activo
2. Aumenta el tamaño del repositorio innecesariamente
3. Puede causar importaciones accidentales de código obsoleto
4. Dificulta el mantenimiento y onboarding de nuevos desarrolladores

## What Changes

- **Eliminar modelos V1 legacy** (9 archivos en `backend/models/`):
  - `models.py` - Modelos antiguos en español (Usuario, Divisa, Categoria, etc.)
  - `models_advanced.py` - Modelos avanzados V1 (TransaccionRecurrente, Activo, etc.)
  - `models_extended.py` - Modelos extendidos V1 (Etiqueta, Adjunto, etc.)
  - `models_config.py` - Configuración V1 (AnioPresupuesto, Configuracion, etc.)
  - `models_wealth.py` - Wealth V1 (WealthSnapshot)
  - `models_layouts.py` - Layouts V1 (UserLayout)
  - `models_notifications.py` - Notificaciones V1 (UserNotification)
  - `models_audit.py` - Audit V1 (integrar contenido útil si existe)
  - `models_criptoya.py` - Mantener (es parte de plugin activo)

- **Eliminar archivos temporales** (raíz y subdirectorios):
  - Scripts de testing temporal (`temp_check_tables.py`, `check_db.py`, etc.)
  - Logs de servidor (`uvicorn.log`, `server.log`)
  - Scripts de debug (`test_endpoints.py`, `start_server.py`)
  - Caché Python (`__pycache__/`, `*.pyc`)
  - Caché pytest (`.pytest_cache/`)

- **Actualizar imports**:
  - Verificar que `models/__init__.py` no referencie archivos eliminados
  - Asegurar que todos los imports apunten a `models_v2`

- **Preservar**:
  - Base de datos SQLite (`3f_app.db`, `3f_system.db`)
  - Archivos de configuración (`.env`, `config.py`)
  - Toda la lógica de API funcional
  - Frontend completo
  - Tests existentes
  - Plugins funcionales

## Capabilities

### Modified Capabilities
- `database-models`: Eliminar dependencias de modelos V1, mantener solo V2

## Impact

- **Backend**: Limpieza de código obsoleto, solo queda código V2 activo
- **Importaciones**: Ninguna, los modelos V1 no son importados por código activo
- **Base de datos**: Sin cambios, las tablas físicas permanecen (se pueden limpiar después si se desea)
- **Tests**: Sin impacto, los tests usan modelos V2
- **Plugins**: Sin impacto, usan modelos V2
- **Frontend**: Sin impacto
