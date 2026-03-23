# Tasks para mejoras-ux

## Tareas Frontend & UI

- [ ] **1. Colapsado de Sidebar** (`specs/temas-customizacion.md`)
  - Modificar las clases CSS/Alpine vinculadas al sidebar-toggler para lograr el estado `sidebar-collapse` visualizando solo iconos en lugar del hide total.

- [ ] **2. Selector de Widgets en Dashboard** (`specs/temas-customizacion.md`)
  - Implementar un panel o modal con listas de checkboxes vinculados al estado visible/oculto de cada bloque de GridStack en el dashboard principal.

- [ ] **3. CRUD de Entidades Financieras** (`specs/core-financiero.md`)
  - Crear la vista de "Entidades Financieras" replicando el layout de categorías.
  - Agregar selector de íconos en el formulario de creación vinculado al Tipo de Entidad.
  - Asegurar binding en el input select del formulario de creación de "Cuentas" para asociar la entidad.

- [ ] **4. Tabla Ledger de Cuentas** (`specs/core-financiero.md`)
  - Reemplazar la vista principal de la ruta `/accounts` en frontend por un formato tabla, incluyendo columnas de Ícono de Banco, Tipo y Balance.

- [ ] **5. Calendario de Recurrentes (Estilo MMEX)** (`specs/transacciones-recurrentes.md`)
  - Integrar FullCalendar (o equivalente) en la vista de recurrentes.
  - Plasmarlas en el calendario basándose en sus iteraciones.
  - Implementar modal popup al realizar un click en un evento del calendario para editarlo o borrarlo, junto con botones flotantes generales.
