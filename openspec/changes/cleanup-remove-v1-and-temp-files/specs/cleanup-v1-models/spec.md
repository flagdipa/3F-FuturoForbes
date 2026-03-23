## ADDED Requirements

### Requirement: Modelos V1 eliminados del codebase
El sistema NO debe contener archivos de modelos legacy (V1) que han sido reemplazados por modelos V2 en `models_v2.py`.

#### Scenario: Archivos V1 inexistentes
- **WHEN** se lista el directorio `backend/models/`
- **THEN** solo deben existir:
  - `__init__.py` (actualizado)
  - `models_v2.py` (modelos principales)
  - `models_criptoya.py` (plugin específico)
- **AND** NO deben existir:
  - `models.py` (legacy en español)
  - `models_advanced.py`
  - `models_extended.py`
  - `models_config.py`
  - `models_wealth.py`
  - `models_layouts.py`
  - `models_notifications.py`
  - `models_audit.py` (contenido revisado e integrado si es necesario)

#### Scenario: Imports funcionando correctamente
- **WHEN** se ejecuta `python -c "from backend.models import *"`
- **THEN** no debe lanzar errores de importación
- **AND** todos los modelos deben estar disponibles desde `models_v2`

### Requirement: Archivos temporales eliminados
El directorio raíz del proyecto NO debe contener archivos temporales de testing, debugging o logs del servidor.

#### Scenario: Archivos temporales inexistentes
- **WHEN** se lista el directorio raíz (`C:\xampp\htdocs\3F`)
- **THEN** NO deben existir:
  - Scripts temporales: `temp_*.py`, `check_*.py`, `test_endpoints.py`, `start_server.py`
  - Logs de servidor: `uvicorn*.log`, `server.log`
  - Archivos Python temporales: `*.pyc`, `__pycache__/`
  - Caché de pytest: `.pytest_cache/`
- **AND** los scripts en `scripts/` deben revisarse para eliminar los que sean puros testing/debug

#### Scenario: Backend tests preservados
- **WHEN** se ejecutan `python -m pytest backend/tests/`
- **THEN** todos los tests deben pasar (15/15)
- **AND** los scripts `backend/tests/test_*.py` deben permanecer

### Requirement: Caché Python limpiado
Todos los directorios `__pycache__/` y archivos `*.pyc` deben ser eliminados recursivamente del proyecto.

#### Scenario: Sin caché Python
- **WHEN** se busca `find . -name "__pycache__" -o -name "*.pyc"`
- **THEN** no debe encontrar resultados
- **AND** el sistema debe funcionar normalmente (los .pyc se regeneran al importar)
