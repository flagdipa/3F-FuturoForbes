## Context

El sistema tiene una dependencia crítica en modelos V1 legacy que bloquea la limpieza completa del codebase. El archivo `backend/api/retro.py` importa y usa `TipoEntidadFinanciera` e `IdentidadFinanciera` desde `models.py`, manteniendo código legacy activo en producción.

**Estado Actual:**
- ✅ Tablas legacy están vacías (0 registros) - no hay datos que migrar
- ✅ Frontend usa endpoints de `retro.py` para funcionalidad de entidades financieras
- ❌ `backend/models/__init__.py` todavía importa modelos legacy
- ❌ `backend/api/retro.py` depende completamente de modelos V1

## Goals / Non-Goals

**Goals:**
- Migrar completamente la funcionalidad de entidades financieras a modelos V2
- Eliminar todas las dependencias a modelos legacy V1
- Mantener compatibilidad total con el frontend existente
- Habilitar la limpieza completa de archivos V1

**Non-Goals:**
- Cambiar la interfaz API existente
- Modificar el comportamiento del frontend
- Migrar datos (no hay datos que migrar)
- Agregar nuevas funcionalidades

## Decisions

### Decisión 1: Usar `Institution.type` para categorización
**Rationale:** En lugar de mantener una tabla separada de tipos (`TipoEntidadFinanciera`), usaremos el campo `type` de `Institution` para categorizar directamente. Esto simplifica la estructura y elimina la necesidad de joins.

### Decisión 2: Mantener estructura de respuesta API
**Rationale:** El frontend espera cierta estructura de datos. Mantendremos la misma estructura de respuesta para garantizar compatibilidad.

### Decisión 3: Eliminar tablas legacy después de migración
**Rationale:** Como las tablas legacy están vacías, podemos eliminarlas con seguridad después de migrar el código.

### Decisión 4: Soft delete para estado "activo"
**Rationale:** En lugar del campo booleano `activo`, usaremos `deleted_at is None` para indicar entidades activas, siguiendo el patrón V2.

## Risks / Trade-offs

**Risk:** Frontend podría romperse si la estructura de respuesta cambia
→ **Mitigation:** Mantener estructura idéntica de respuesta API

**Risk:** Pérdida de funcionalidad de tipos detallada
→ **Mitigation:** Los tipos se convierten en strings simples ("Bancos", "Billeteras"), suficiente para UI

**Risk:** Errores en mapeo de campos
→ **Mitigation:** Tests exhaustivos de todos los endpoints migrados

**Trade-off:** Simplicidad vs. flexibilidad
- ✅ Ganamos: Código más simple, menos tablas, mejor performance
- ⚠️ Perdemos: Capacidad de tener metadatos ricos por tipo (descripción, icono, color)
- **Decisión:** Aceptable - los metadatos de tipos pueden manejarse en el frontend

## Migration Plan

1. **Fase 1:** Migrar código en `backend/api/retro.py`
   - Actualizar imports
   - Reemplazar modelos legacy por `Institution`
   - Mantener estructura de respuesta API

2. **Fase 2:** Actualizar dependencias
   - Eliminar imports legacy de `backend/models/__init__.py`
   - Verificar que no hay más referencias

3. **Fase 3:** Limpieza
   - Eliminar `backend/models/models.py`
   - Eliminar tablas legacy de la base de datos (opcional)

4. **Fase 4:** Verificación
   - Tests completos
   - Verificación manual de funcionalidad

**Rollback:** Si algo sale mal, restaurar `backend/api/retro.py` desde git

## Open Questions

1. ¿El frontend usa los campos `icono` y `color` de los tipos? → Si es así, necesitamos preservar esta información de alguna manera.
2. ¿Hay algún otro lugar en el código que use `TipoEntidadFinanciera` o `IdentidadFinanciera`? → Buscar exhaustivamente antes de eliminar.
3. ¿Las tablas legacy deben eliminarse físicamente de la base de datos? → Sí, pero después de verificar que la migración funciona.