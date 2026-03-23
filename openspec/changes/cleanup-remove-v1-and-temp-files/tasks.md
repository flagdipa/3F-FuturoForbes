# Tasks: Limpieza de Archivos V1 y Temporales

## Fase 1: Identificación y Backup (Preparación)
- [x] 1.1 Crear lista completa de archivos V1 a eliminar
- [x] 1.2 Crear lista de archivos temporales en raíz
- [x] 1.3 Verificar que tests funcionan antes de cambios
- [x] 1.4 Confirmar que models_v2.py contiene todos los modelos necesarios

## Fase 2: Eliminación de Modelos V1 Legacy
- [x] 2.1 Eliminar `backend/models/models.py` (modelos legacy español)
- [x] 2.2 Eliminar `backend/models/models_advanced.py`
- [x] 2.3 Eliminar `backend/models/models_extended.py`
- [x] 2.4 Eliminar `backend/models/models_config.py`
- [x] 2.5 Eliminar `backend/models/models_wealth.py`
- [x] 2.6 Eliminar `backend/models/models_layouts.py`
- [x] 2.7 Eliminar `backend/models/models_notifications.py`
- [x] 2.8 Revisar `backend/models/models_audit.py` - integrar contenido útil a V2 si existe, luego eliminar
- [x] 2.9 Actualizar `backend/models/__init__.py` para remover imports de archivos eliminados

## Fase 3: Eliminación de Archivos Temporales (Raíz)
- [x] 3.1 Eliminar `temp_check_tables.py`
- [x] 3.2 Eliminar `check_db.py`
- [x] 3.3 Eliminar `test_endpoints.py`
- [x] 3.4 Eliminar `start_server.py`
- [x] 3.5 Eliminar `server.log`
- [x] 3.6 Eliminar `uvicorn.log`
- [x] 3.7 Eliminar `uvicorn_err.log`
- [x] 3.8 Eliminar `uvicorn_debug.log`
- [x] 3.9 Eliminar `uvicorn_debug_err.log`
- [x] 3.10 Eliminar `uvicorn_final.log`
- [x] 3.11 Eliminar archivo con nombre corrupto `C:xampphtdocs3Fopenspecchangessystem-end-to-end-verificationserver.log`

## Fase 4: Limpieza de Scripts Temporales
- [x] 4.1 Revisar y eliminar `scripts/test_ocr_exec.py` (testing temporal)
- [x] 4.2 Revisar y eliminar `scripts/test_ocr_status.py` (testing temporal)
- [x] 4.3 Revisar y eliminar `scripts/test_reconciliation_manual.py` (testing temporal)
- [x] 4.4 Revisar y eliminar `scripts/debug_paddle.py` (debug temporal)
- [x] 4.5 Revisar `scripts/fix_payee_schema.py` - eliminar si ya no es necesario
- [x] 4.6 Revisar `scripts/fix_phase14_schema.py` - eliminar si ya no es necesario
- [x] 4.7 Revisar `backend/scripts/check_plugins_db.py` - contiene URL hardcodeada de MySQL, eliminar o actualizar

## Fase 5: Limpieza de Caché Python
- [x] 5.1 Eliminar `.pytest_cache/` en raíz
- [x] 5.2 Eliminar `__pycache__/` en backend/
- [x] 5.3 Eliminar `__pycache__/` en backend/api/
- [x] 5.4 Eliminar `__pycache__/` en backend/models/
- [x] 5.5 Eliminar `__pycache__/` en backend/core/
- [x] 5.6 Eliminar archivos `*.pyc` en todo el proyecto (excepto .venv)
- [x] 5.7 Eliminar `logs/app.log` y `logs/error.log` si son temporales
- [x] 5.8 Eliminar `backend/logs/app.log` y `backend/logs/error.log` si son temporales

## Fase 6: Verificación Final
- [x] 6.1 Ejecutar tests: `python -m pytest backend/tests/ -v`
- [x] 6.2 Verificar imports: `python -c "from backend.models import *"`
- [x] 6.3 Verificar servidor inicia: `python -c "from backend.main import app"`
- [x] 6.4 Confirmar no quedan archivos V1: `ls backend/models/`
- [x] 6.5 Confirmar no quedan logs temporales en raíz
- [x] 6.6 Verificar que los scripts útiles permanecen:
  - `scripts/seed_demo_data.py` (preservar)
  - `scripts/seed_all.py` (preservar)
  - `scripts/verify_features.py` (preservar)
  - `scripts/register_backup_plugin.py` (preservar)
  - `scripts/register_criptoya_plugin.py` (preservar)
  - `backend/scripts/init_db.py` (preservar)

## Fase 7: Documentación
- [x] 7.1 Actualizar INFORME_ESTADO_SISTEMA_3F.md con estructura limpia
- [x] 7.2 Crear nota sobre modelos eliminados (referencia histórica)
- [x] 7.3 Verificar README.md refleja estructura actual

---
