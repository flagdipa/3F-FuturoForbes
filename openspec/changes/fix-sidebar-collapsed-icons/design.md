# Design: Sidebar Icons in Collapsed Mode

## Context

El sistema 3F utiliza AdminLTE 4 como framework de UI, el cual incluye un sidebar de navegación con capacidad de colapsarse. El modo colapsado debería mostrar solo los íconos Font Awesome centrados en un ancho reducido (~54-70px), permitiendo al usuario acceder rápidamente a las funciones principales.

Actualmente, cuando el sidebar se colapsa mediante el botón de toggle o en dispositivos móviles, los íconos no se visualizan correctamente. El problema parece estar en la cascada CSS donde los estilos del modo colapsado no están aplicando correctamente las propiedades de visibilidad y centrado a los elementos `.nav-icon`.

El CSS actual en `neon-3f.css` tiene reglas definidas para `.sidebar-collapse .app-sidebar .nav-icon` pero es posible que estén siendo sobrescritas por estilos de AdminLTE o que falten propiedades específicas para Font Awesome.

## Goals / Non-Goals

**Goals:**
- Asegurar que los íconos Font Awesome sean visibles cuando el sidebar está colapsado
- Centrar los íconos horizontalmente en el ancho reducido del sidebar
- Mantener los tooltips funcionales que muestran el nombre de la sección al hacer hover
- Preservar el comportamiento actual del sidebar expandido (sin regresiones)
- Soportar tanto modo colapsado en desktop como off-canvas en mobile

**Non-Goals:**
- No se modificará la estructura HTML del sidebar (salvo sea absolutamente necesario)
- No se agregarán nuevas dependencias (Font Awesome ya está incluido)
- No se modificará la funcionalidad de los submenús (treeview)
- No se realizarán cambios al sistema de temas o colores existentes

## Decisions

### 1. Estrategia CSS-First
**Decisión:** Resolver el problema puramente mediante ajustes CSS sin modificar JavaScript.

**Rationale:**
- El problema es de estilos, no de lógica
- Alpine.js y el sidebar-manager.js funcionan correctamente para el estado del sidebar
- Cambios CSS son menos propensos a introducir bugs funcionales
- AdminLTE maneja el toggle del sidebar mediante clases CSS que ya existen

**Alternativas consideradas:**
- Modificar sidebar-manager.js para agregar/quitar clases dinámicamente: Rechazado - añade complejidad innecesaria
- Reescribir el componente de sidebar: Rechazado - demasiado riesgo para un fix puntual

### 2. Prioridad de Selectores CSS
**Decisión:** Utilizar selectores de alta especificidad para sobreescribir estilos de AdminLTE.

**Implementación:**
```css
/* En lugar de */
.sidebar-collapse .nav-icon { }

/* Usar */
.sidebar-collapse .app-sidebar .nav-link .nav-icon,
.app-sidebar.sidebar-collapse .nav-link .nav-icon { }
```

**Rationale:** AdminLTE aplica estilos con cierta especificidad. Necesitamos asegurar que nuestros estilos para el modo colapsado tengan mayor prioridad.

### 3. Enfoque Responsive Dual
**Decisión:** Tratar desktop y mobile por separado.

**Rationale:**
- Desktop: sidebar colapsado mini (~54-70px) con íconos centrados
- Mobile: sidebar off-canvas (se oculta completamente, se muestra con overlay)
- Los íconos solo necesitan fix en el modo colapsado de desktop
- En mobile, cuando el sidebar se abre, se muestra completo (no hay modo "mini")

## Risks / Trade-offs

**[Riesgo] Regresión en estilos del sidebar expandido**
→ Mitigación: Las reglas CSS específicas usan la clase `.sidebar-collapse` que solo aplica cuando el sidebar está colapsado. El modo expandido no usa esta clase.

**[Riesgo] Conflictos con futuras actualizaciones de AdminLTE**
→ Mitigación: Usar comentarios claros en el CSS indicando que son overrides específicos. Las reglas están bien encapsuladas.

**[Riesgo] Íconos de diferentes tamaños no se alinean correctamente**
→ Mitigación: Forzar dimensiones consistentes con `width`, `height`, `min-width`, `text-align: center` y `display: flex` en el contenedor.

**[Riesgo] Tooltips no funcionan en mobile (touch)**
→ Mitigación: Los tooltips CSS con `:hover` y `:after` solo funcionan en desktop. En mobile el sidebar se muestra completo (no colapsado), por lo que los labels son visibles.

## Open Questions

1. **¿El problema afecta todos los navegadores?** → Requiere testing en Chrome, Firefox, Safari
2. **¿Los íconos tienen tamaños diferentes según su clase Font Awesome?** → Verificar si `fa-lg`, `fa-sm` afectan el centrado
3. **¿Existen íconos que no usen la clase `.nav-icon`?** → Revisar si hay íconos en el sidebar que usen clases directamente sin el wrapper

