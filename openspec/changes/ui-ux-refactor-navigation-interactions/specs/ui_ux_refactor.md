# Spec: Refactor de Navegación e Interacciones UI/UX

## ADDED Requirements

### Requirement: Botones de Acción Estilizados y Alineados
Al pie de las vistas de gestión (como Transacciones), los botones de acción principal (Nuevo, Editar, Duplicar, Borrar) deben estar alineados al centro y presentar un tamaño visualmente equivalente.

#### Scenario: Botones de Transacción
- **GIVEN** Un usuario en la página de Transacciones
- **WHEN** Visualiza la barra de acciones inferior
- **THEN** Los botones tienen un `min-width` uniforme (~120px)
- **AND** Los botones están centrados horizontalmente en su contenedor

---

### Requirement: Edición de Transacción mediante Doble Clic
El sistema debe permitir abrir el formulario de edición de una transacción al realizar doble clic sobre cualquier fila de la tabla principal.

#### Scenario: Doble Clic en Fila de Transacción
- **GIVEN** Un usuario en la tabla de Transacciones con varias entradas
- **WHEN** Realiza doble clic sobre una fila determinada
- **THEN** El modal de edición de esa transacción se abre automáticamente
- **AND** Los datos precargados corresponden a la transacción seleccionada

---

### Requirement: Acceso Centralizado a Entidades y Cuentas
La gestión de entidades maestras (Beneficiarios y Categorías) debe estar disponible desde un menú superior dedicado, eliminando su redundancia en el sidebar.

#### Scenario: Acceso desde Menú Superior
- **GIVEN** El usuario observa la barra de navegación superior (Topbar)
- **WHEN** Despliega el menú "Entidades y Cuentas" (ícono de edificio/banco)
- **THEN** Ve las opciones de "Gestión de Beneficiarios" y "Gestión de Categorías"
- **AND** Ambas opciones disparan sus respectivos administradores (modales o vistas)
- **AND** La sección "Catálogos" ya no es visible en el sidebar
