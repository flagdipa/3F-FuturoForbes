# Proposal: Emergency UI Layout Fix & Relocate Tools

## Problem Context
En los recientes despliegues de UI, se duplicaron y desorganizaron los accesos a "Beneficiarios" y "Categorías", colocándolos tanto en el menú lateral (Sidebar) como en un menú desplegable superior (Top Menu).
Esta redundancia y sobrecarga de elementos en el Sidebar provocó que el diseño de AdminLTE se "desconfigure" visualmente, empujando elementos y generando un frontend confuso. Además, los eventos de apertura de modales Alpine no coincidían entre ambos menús, rompiendo la funcionalidad.

## Proposed Solution
Atender el reporte urgente del UX/UI:
1. **Limpiar el Sidebar**: Eliminar por completo el bloque "HERRAMIENTAS" (Beneficiarios y Categorías) del menú lateral.
2. **Consolidar en el Menú Superior**: Mover y estabilizar los accesos a los gestores de "Beneficiarios" y "Categorías" exclusivamente en el menú superior (Top Navbar), como solicitó explícitamente el usuario.
3. **Corregir Eventos Modales**: Asegurarnos de que los botones del menú superior disparen correctamente los eventos `CustomEvent('open-beneficiaries')` y `CustomEvent('open-categories')` para abrir las modales sin recargar la página.
4. **Optimizar Sidebar**: Corregir cualquier desbordamiento o HTML mal formado (anidación incorrecta de AdminLTE treeviews) que esté provocando la desconfiguración reportada por el usuario.

## Impact
- **Archivos Modificados**: `frontend/templates/base.html`
- **Frontend**: El Sidebar será más ligero y estético. Las herramientas de gestión se abrirán de forma nativa desde el navbar superior.
- **Sin regresiones backend**: Esto es un fix puramente de capa vista/UI.
