## Context

El sistema 3F ha completado la migración a la arquitectura V2. Los modelos V1 en español (Usuario, Cuenta, etc.) han sido reemplazados por modelos V2 en inglés (User, Account, etc.) unificados en `models_v2.py`. Además, durante el desarrollo se acumularon archivos temporales de testing y debugging que ya no son necesarios.

Esta limpieza es necesaria para:
1. Mantener el codebase limpio y profesional
2. Eliminar confusión sobre qué código está activo
3. Reducir el tamaño del repositorio
4. Prevenir importaciones accidentales de código obsoleto

## Goals / Non-Goals

**Goals:**
- Eliminar todos los archivos de modelos V1 legacy
- Limpiar archivos temporales de la raíz del proyecto
- Eliminar caché Python y logs temporales
- Verificar que el sistema sigue funcionando después de la limpieza
- Actualizar imports en models/__init__.py

**Non-Goals:**
- Modificar la lógica de negocio existente
- Cambiar la estructura de la base de datos (las tablas físicas permanecen)
- Eliminar tests funcionales (backend/tests/)
- Eliminar scripts útiles de seeding y registro
- Eliminar plugins funcionales

## Decisions

### Decisión 1: Preservar models_criptoya.py
**Rationale:** Este archivo contiene modelos específicos del plugin CriptoYa que está activo y funcionando. No es parte de los modelos V1 legacy.

### Decisión 2: Eliminar solo archivos puramente temporales
**Rationale:** Algunos scripts en `scripts/` son útiles (seed_demo_data.py, register plugins) y deben preservarse. Solo eliminar los que son claramente temporales de testing/debug.

### Decisión 3: Mantener tablas físicas en SQLite
**Rationale:** Aunque eliminamos los archivos .py de modelos V1, las tablas físicas en la base de datos SQLite pueden permanecer. Si se desea limpieza completa, se requeriría migración de datos, pero eso es fuera del scope de esta tarea.

### Decisión 4: No eliminar __pycache__ de .venv
**Rationale:** El directorio `.venv` es el entorno virtual y sus archivos de caché son gestionados por pip. Solo limpiar caché del código del proyecto, no de dependencias.

## Risks / Trade-offs

**Risk:** Alguien podría estar importando modelos V1 desde algún lugar no detectado
→ **Mitigation:** Verificar con grep antes de eliminar. Si hay imports, migrarlos a V2 primero.

**Risk:** Scripts útiles podrían ser eliminados por error
→ **Mitigation:** Lista explícita de scripts a preservar. Revisar cada uno individualmente.

**Risk:** Tests podrían fallar después de la limpieza
→ **Mitigation:** Ejecutar tests completos después de cada fase de eliminación.

**Risk:** Archivos con nombres corruptos no se eliminan correctamente
→ **Mitigation:** Verificar eliminación manual si es necesario.

## Migration Plan

1. **Fase 1:** Preparación y verificación (backup implícito con git)
2. **Fase 2:** Eliminar modelos V1 (alta prioridad)
3. **Fase 3:** Eliminar temporales raíz (media prioridad)
4. **Fase 4:** Revisar scripts (media prioridad)
5. **Fase 5:** Limpiar caché (baja prioridad, puede regenerarse)
6. **Fase 6:** Verificación completa
7. **Fase 7:** Documentar cambios

**Rollback:** Si algo falla, restaurar desde git: `git checkout -- <archivo>`

## Open Questions

1. ¿El archivo `backend/scripts/check_plugins_db.py` con URL hardcodeada de MySQL se usa en algún lugar? → Verificar y eliminar o actualizar.
2. ¿Hay algún código que importe desde models.py directamente (no via models/__init__.py)? → Buscar antes de eliminar.
