# Tasks: Refactor de Navegación e Interacciones UI/UX

## 1. Estilos y Layout

- [x] 1.1 Agregar la clase `.btn-action-standard` en `neon-3f.css` para unificación de botones (min-width, flex centrado, etc.).
- [x] 1.2 Actualizar el contenedor de botones en `transactions.html` para unificar los tamaños utilizando la nueva clase.
- [x] 1.3 Revisar otros pie de página (ej. `beneficiaries.html`, `categories.html`) para aplicar la misma consistencia de botones.

## 2. Consolidación de JavaScript

- [x] 2.1 Identificar y consolidar las dos definiciones de `editTransaction` en `static/js/transactions.js`.
- [x] 2.2 Refactorizar `editTransaction` para que acepte tanto un objeto ID como un objeto completo para mayor robustez heredada de Alpine.
- [x] 2.3 Verificar que el evento `@dblclick` en la fila de la tabla en `transactions.html` dispara correctamente la función consolidada.

## 3. Navegación Topbar y Sidebar

- [x] 3.1 Modificar `base.html` para remover la sección `<li class="nav-item">...Catálogos...</li>` del sidebar.
- [x] 3.2 Renombrar elDropdown de herramientas en el navbar a "Entidades y Cuentas" y actualizar su ícono.
- [x] 3.3 Agregar accesos directos de "Gestión de Beneficiarios" y "Gestión de Categorías" al nuevo menú superior si no estaban integrados completamente.
- [x] 3.4 Asegurar las traducciones de las nuevas etiquetas en `lang-es.json` y `lang-en.json`.

## 4. Validación

- [x] 4.1 Verificar Visualmente la alineación y tamaño de botones en escritorio y móvil.
- [x] 4.2 Probar funcionalmente el doble clic en al menos 5 transacciones diferentes.
- [x] 4.3 Confirmar que los menús del navbar funcionan correctamente y disparan sus acciones/modales.
