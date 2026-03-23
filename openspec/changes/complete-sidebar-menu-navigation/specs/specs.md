# Specs: Complete Sidebar Menu Navigation

## BDD Requirements

### Requirement: Añadir ítems faltantes al Menú Lateral
- **GIVEN** un usuario autenticado visualizando el dashboard o cualquier otra pantalla
- **WHEN** el usuario despliega o ve el sidebar principal
- **THEN** deben estar visibles como opciones principales: Cuentas, Gestores (Beneficiarios y Categorías), Planificación (Presupuestos, Metas de Ahorro), Reportes, Inversiones, Mercado y Configuración.
- **AND** cada bloque/ícono debe ajustarse al esquema semántico AdminLTE (`nav-icon`, `fa-xxx`, clase text-* representativa).

### Requirement: Soporte Tooltips para íconos colapsados (Desktop)
- **GIVEN** un Sidebar en modo colapsado (`sidebar-collapse` en el body)
- **WHEN** el usuario pasa el cursor sobre cualquiera de los nuevos íconos (Ej: `fa-wallet` de Cuentas)
- **THEN** aparece un tooltip a la derecha con el Label correspondiente gracias al atributo dinámico `:data-label="$store.lang.t('nav.X')"`.

### Requirement: Traducción de Nuevos Elementos
- **GIVEN** que el usuario cambia el idioma a través de `$store.lang.switch('en')` o `('es')`
- **WHEN** interactúa con el Sidebar
- **THEN** todos los textos de navegación (Reportes, Mercado, Metas de Ahorro) cambian dinámicamente.
- **AND** los tooltips (`data-label`) también reflejan el idioma activo mediante Alpine.

### Requirement: Comportamiento del Gestor de Entidades UI
- **GIVEN** los ítems de navegación de "Beneficiarios" y "Categorías"
- **WHEN** un usuario hace clic en el enlace del sidebar
- **THEN** no ocurre un cambio de hipervínculo completo (Page Reload)
- **AND** en su lugar, se lanza el evento Alpine modal nativo: `$dispatch('open-modal', 'beneficiaries-modal')` o `$dispatch('open-category-modal')`, revelando los modales ya implementados en el DOM (`base.html`).

### Requirement: Navegación Agrupada (Treeview AdminLTE)
- **GIVEN** que el sidebar tiene limitaciones de espacio vertical
- **WHEN** se implementan secciones jerárquicas (Cuentas, Reportes, Mercado)
- **THEN** se utiliza la convención `.nav-treeview` y `data-lte-toggle="treeview"` en el `<li>` padre.
- **AND** hacer clic en el padre expande sus hijos sin cambiar de página, y hacer clic en un hijo invoca la URL correcta de destino.
