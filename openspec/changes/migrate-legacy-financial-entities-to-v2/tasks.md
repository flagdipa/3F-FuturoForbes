# Tasks: Migrar Entidades Financieras Legacy a V2

## Fase 1: Preparación y Análisis
- [ ] 1.1 Analizar estructura actual de `backend/api/retro.py`
- [ ] 1.2 Identificar todos los endpoints que usan modelos legacy
- [ ] 1.3 Crear mapeo de campos legacy → V2
- [ ] 1.4 Verificar que no hay datos en tablas legacy (confirmado: 0 registros)

## Fase 2: Migración de Código
- [ ] 2.1 Actualizar imports en `backend/api/retro.py`:
  - ❌ Eliminar: `from ..models.models import TipoEntidadFinanciera, IdentidadFinanciera`
  - ✅ Agregar: `from ..models.models_v2 import Institution`

- [ ] 2.2 Eliminar clases DTO legacy:
  - ❌ `RetroTipoEntidadIn`
  - ❌ `RetroEntidadIn`

- [ ] 2.3 Crear nuevas clases DTO V2:
  - ✅ `InstitutionTypeIn` (para tipos)
  - ✅ `InstitutionIn` (para instituciones)

- [ ] 2.4 Migrar endpoint `/financial-entities/types`:
  - ✅ Usar `Institution` con `type="Bancos"`, `type="Billeteras Virtuales"`, etc.
  - ✅ Mantener misma interfaz API

- [ ] 2.5 Migrar endpoint `/financial-entities/institutions`:
  - ✅ Usar `Institution` en lugar de `IdentidadFinanciera`
  - ✅ Mantener misma interfaz API
  - ✅ Mapear campos:
    - `nombre` → `name`
    - `sucursal` → `branch`
    - `direccion` → `address`
    - `web` → `website`
    - `contacto` → `contact`
    - `telefono` → `phone`
    - `cuit` → `cuit` (mantener)

- [ ] 2.6 Actualizar endpoint `/financial-entities/seed`:
  - ✅ Crear `Institution` en lugar de `TipoEntidadFinanciera`
  - ✅ Usar formato V2 para datos semilla

- [ ] 2.7 Actualizar lógica de relaciones:
  - ✅ Reemplazar `id_tipo` por lógica de tipos incorporada
  - ✅ Usar `Institution.type` para categorización

## Fase 3: Limpieza de Dependencias
- [ ] 3.1 Actualizar `backend/models/__init__.py`:
  - ❌ Eliminar: `from .models import TipoEntidadFinanciera, IdentidadFinanciera`
  - ❌ Eliminar estas clases de `metadata_models`

- [ ] 3.2 Verificar que no hay más imports legacy en todo el proyecto
- [ ] 3.3 Eliminar `backend/models/models.py` (contiene modelos legacy)

## Fase 4: Verificación
- [ ] 4.1 Ejecutar tests: `python -m pytest backend/tests/ -v`
- [ ] 4.2 Verificar que API sigue funcionando:
  - ✅ `GET /financial-entities/types`
  - ✅ `GET /financial-entities/institutions`
  - ✅ `POST /financial-entities/types`
  - ✅ `POST /financial-entities/institutions`
  - ✅ `POST /financial-entities/seed`

- [ ] 4.3 Verificar que frontend no se ve afectado
- [ ] 4.4 Confirmar que no hay más referencias a modelos legacy

## Fase 5: Documentación
- [ ] 5.1 Actualizar `INFORME_ESTADO_SISTEMA_3F.md` con la migración completada
- [ ] 5.2 Documentar cambios en API (si hay diferencias significativas)

---

## Mapeo de Campos

### Tipos de Entidad (Legacy → V2)
- `nombre_tipo` → `Institution.type` (ej: "Bancos", "Billeteras Virtuales")
- `icono` → `Institution.icon` (ej: "fa-university", "fa-wallet")
- `color` → (integrar en nombre o eliminar - V2 usa tema CSS)
- `activo` → `Institution.deleted_at is None` (soft delete)
- `descripcion` → (eliminar o integrar en lógica de UI)

### Instituciones (Legacy → V2)
- `nombre` → `Institution.name`
- `id_tipo` → `Institution.type` (string directo)
- `sucursal` → `Institution.branch`
- `direccion` → `Institution.address`
- `web` → `Institution.website`
- `contacto` → `Institution.contact`
- `telefono` → `Institution.phone`
- `cuit` → `Institution.cuit`
- `activo` → `Institution.deleted_at is None`
- `logo_url` → `Institution.icon` (si aplica)

---

## Notas Importantes

- ✅ **No hay datos que migrar** (tablas legacy están vacías)
- 🔧 **Frontend compatibility**: Mantener misma estructura de respuesta API
- 🚀 **Performance**: V2 es más eficiente sin joins de tablas de tipos
- 🧹 **Clean code**: Eliminar ~200 líneas de código legacy
- 📦 **Reduced dependencies**: Eliminar 2 modelos legacy complejos

## Riesgos y Mitigación

- **Riesgo**: Frontend podría esperar campos específicos
  - **Mitigación**: Mantener misma estructura de respuesta API

- **Riesgo**: Errores en mapeo de campos
  - **Mitigación**: Tests exhaustivos de todos los endpoints

- **Riesgo**: Funcionalidad de seed no crea datos correctos
  - **Mitigación**: Verificar manualmente después de migración