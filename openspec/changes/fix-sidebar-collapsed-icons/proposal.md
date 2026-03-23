# Proposal: Fix Sidebar Icons When Collapsed

## Why

El sidebar de navegación tiene un modo colapsado que debería mostrar únicamente los íconos de Font Awesome sin texto, facilitando el acceso rápido a las funciones principales y ahorrando espacio en pantalla. Actualmente, cuando el sidebar se colapsa (se reduce a ~54-70px de ancho), los íconos no se renderizan correctamente o no son visibles, lo que impide la navegación efectiva en este modo.

El problema afecta la experiencia de usuario, especialmente en pantallas donde el espacio es limitado, ya que el modo colapsado se vuelve inutilizable sin íconos visibles.

## What Changes

- Corregir el CSS del sidebar colapsado para asegurar que los íconos Font Awesome (`fa-solid`, `fa-*`) sean visibles y centrados
- Ajustar los estilos de `nav-icon` en modo colapsado para garantizar tamaño adecuado y alineación
- Verificar que los tooltips con `data-label` funcionen correctamente al hacer hover sobre los íconos
- Asegurar que los submenús (nav-treeview) no interfieran con la visualización de íconos
- Aplicar estilos específicos para diferentes breakpoints (desktop vs mobile)
- **BREAKING**: Posibles cambios en las clases CSS del sidebar si es necesario reestructurar

## Capabilities

### New Capabilities
- `sidebar-collapsed-icons`: Corrección de visibilidad y centrado de íconos en sidebar colapsado

### Modified Capabilities
- *(Ninguna capacidad existente modifica sus requisitos de comportamiento)*

## Impact

- **Archivos afectados**:
  - `frontend/static/css/neon-3f.css` - Estilos principales del sidebar
  - `frontend/templates/base.html` - Estructura del sidebar (posible ajuste de clases)
  - Posiblemente `frontend/static/js/sidebar-manager.js` - Si necesita ajustes de Alpine.js

- **UI/UX**: Mejor experiencia de navegación en modo colapsado
- **Compatibilidad**: Mantiene compatibilidad con AdminLTE 4
- **Accesibilidad**: Los tooltips mejoran la accesibilidad al mostrar etiquetas al hacer hover

