# Design: Refactor Menú Herramientas y Entidades

## Context

El sistema 3F actual tiene un menú superior con un dropdown "Herramientas" que incluye texto. Esta propuesta busca simplificar la UI eliminando el texto y mostrando solo el ícono. Además, se reestructura el acceso a "Tipos de Financiera" moviéndolo desde el menú superior hacia la ventana de gestión de entidades, donde tiene más sentido contextualmente.

## Goals / Non-Goals

**Goals:**
- Simplificar el menú superior eliminando texto innecesario
- Mover "Tipos de Entidad" al contexto apropiado (ventana de entidades)
- Actualizar terminología para usar "Entidades" en lugar de "Financieras"
- Mantener todas las funcionalidades existentes

**Non-Goals:**
- No se modifica la funcionalidad de gestión de entidades
- No se elimina ninguna funcionalidad, solo se reubica
- No se cambia la estructura de datos del backend

## Decisions

### 1. Simplificación del Menú Herramientas
**Decisión:** Eliminar el texto "Herramientas" y dejar solo el ícono `fa-screwdriver-wrench`

**Implementación:**
```html
<!-- ANTES -->
<a class="nav-link dropdown-toggle" href="#" id="toolsDropdown">
  <i class="fa-solid fa-screwdriver-wrench me-1"></i> 
  <span x-text="$store.lang.t('common.tools')">Herramientas</span>
</a>

<!-- DESPUÉS -->
<a class="nav-link" href="#" id="toolsDropdown" title="Herramientas">
  <i class="fa-solid fa-screwdriver-wrench"></i>
</a>
```

**Rationale:** Menos texto = interfaz más limpia. El ícono es suficientemente descriptivo.

### 2. Reubicación de "Tipos de Entidad"
**Decisión:** Mover la opción desde el menú dropdown a la ventana de entidades

**Implementación:**
- Eliminar del menú dropdown en base.html
- Agregar botón/ícono en la ventana de entidades (entidades/index.html)
- El botón abre la misma URL: `/entidades#tipos`

**Rationale:** "Tipos de Entidad" es una configuración relacionada con entidades, por lo que tiene más sentido contextual estar en la ventana de gestión de entidades.

### 3. Actualización de Terminología
**Decisión:** Cambiar "Financieras" por "Entidades" en todo el diccionario español

**Cambios necesarios:**
```json
// lang-es.json
"tools_mgmt": "Gestión de Entidades"  // antes: "Gestión de Financieras"
"entity_types": "Tipos de Entidad"     // antes: "Tipos de Financiera"
```

**Rationale:** "Entidades" es más genérico y apropiado que "Financieras", cubre mejor el concepto de identidades/instituciones.

## Risks / Trade-offs

**[Riesgo] Usuarios no encuentran "Tipos de Entidad"**
→ Mitigación: Agregar un ícono prominente en la ventana de entidades con tooltip descriptivo

**[Riesgo] Cambio de terminología confunde a usuarios existentes**
→ Mitigación: El cambio es solo en la UI, las URLs y funcionalidad permanecen iguales

**[Riesgo] El ícono solo no es suficientemente intuitivo**
→ Mitigación: Agregar atributo `title` para mostrar tooltip nativo del navegador

