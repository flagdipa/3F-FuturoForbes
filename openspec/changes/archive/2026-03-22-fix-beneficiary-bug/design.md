## Context

El sistema de beneficiarios (Payees) presenta incompatibilidades entre el frontend y backend que impiden la correcta funcionalidad de auto-categorización y el filtrado de transacciones.

**Estado actual:**
- Backend (`payees.py`): Usa modelo `Payee` con campos: `name`, `code`, `default_category_id`, `bank_name`, `cbu`, `cuit`, `notes`
- Frontend (`beneficiary-manager.js`): Usa campos en español: `nombre_beneficiario`, `cbu`, `cuit`, `telefono`, `direccion`, `banco`, `sitio_web`, `notas`, `activo` - pero **falta** `default_category_id` y `code`
- El campo `sitio_web` no existe en el modelo del backend
- Los nombres de campos no coinciden entre frontend y backend

**Problemas identificados:**
1. Campo `default_category_id` no se maneja en el frontend (impide auto-categorización)
2. Campo `code` no se genera ni se maneja en el frontend
3. Campo `sitio_web` no existe en el backend pero sí en el frontend
4. Mapeo de campos inconsistente (`nombre_beneficiario` vs `name`, `banco` vs `bank_name`)
5. Campos `telefono` y `direccion` no existen en el modelo del backend

## Goals / Non-Goals

**Goals:**
- Corregir el manejo de `default_category_id` en frontend y backend
- Agregar generación automática del campo `code` para nuevos beneficiarios
- Sincronizar los nombres de campos entre frontend y backend
- Validar que el filtrado de transacciones por beneficiario funcione end-to-end
- Asegurar que la auto-categorización funcione al crear transacciones

**Non-Goals:**
- No modificar el esquema de base de datos (tabla `payees`)
- No agregar campos nuevos al modelo (telefono, direccion, sitio_web se mantienen como extras ignorados)
- No modificar la arquitectura del plugin manager

## Decisions

**Decision 1: Mapeo de campos frontend→backend**
- Opción A: Cambiar frontend a inglés
- Opción B: Agregar mapeo en el backend para aceptar nombres en español
- **Elegida: Opción A** - Cambiar el frontend para usar los nombres de campos del backend (name, code, default_category_id, etc.)
- **Rationale:** Mantiene consistencia con la API REST y evita duplicar lógica de mapeo en múltiples lugares

**Decision 2: Generación del campo `code`**
- **Estrategia:** Generar automáticamente a partir del nombre usando: `nombre.toLowerCase().replace(/[^a-z0-9]/g, '_')[:20]`
- **Lugar:** En el frontend al crear nuevo beneficiario, o en el backend si viene vacío
- **Rationale:** Asegura unicidad y consistencia sin require input del usuario

**Decision 3: Manejo de campos extra (`telefono`, `direccion`, `sitio_web`)**
- **Estrategia:** Almacenar en campo `notes` como JSON si no existen columnas dedicadas
- **Alternativa:** Ignorar estos campos (pérdida de datos)
- **Elegida:** Opción 1 - Almacenar en `notes` como metadata JSON
- **Rationale:** Preserva la información del usuario sin requerir migración de BD

**Decision 4: Carga de categorías para dropdown**
- **Implementar:** Endpoint `/api/v1/categories` ya existe, usarlo para poblar dropdown de categoría por defecto
- **Rationale:** Reutilizar infraestructura existente

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Cambios en frontend rompen otras partes que usan beneficiarios | Buscar todos los usos de campos en español antes de modificar |
| Código auto-generado puede colisionar | Agregar timestamp o UUID si el código basado en nombre ya existe |
| Datos existentes con campos extra en notes necesitan migración | Script de migración opcional para extraer telefono/direccion de notes si existen |
| Auto-categorización puede no funcionar si la categoría default se borra | Validar que la categoría existe antes de asignarla a una transacción |

## Migration Plan

1. **Phase 1**: Actualizar frontend para usar campos correctos del backend
2. **Phase 2**: Agregar manejo de `default_category_id` con dropdown de categorías
3. **Phase 3**: Implementar generación automática de `code`
4. **Phase 4**: Actualizar formulario de transacciones para usar auto-categorización
5. **Phase 5**: Validación end-to-end y tests

**Rollback:** Revertir commits de git si surge problema crítico
