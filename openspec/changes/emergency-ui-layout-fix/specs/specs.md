# Specs: Emergency UI Layout Fix & Relocate Tools

## BDD Requirements

### Requirement: Simplificar Sidebar y remover items Tools
- **GIVEN** que existe una larga lista de elementos en la navbar lateral que rompe la disposición visual
- **WHEN** un usuario despliega la app
- **THEN** ya NO debe existir en el lateral izquierdo las opciones directas ni el sub-header de "Herramientas" (Categorías y Beneficiarios).
- **AND** como consecuencia la Sidebar debe renderizarse más estéticamente y sin problemas de overflow.

### Requirement: Opciones de Beneficiarios o Categorías en Menú Superior
- **GIVEN** una estructura de `<nav class="app-header">` con un botón dropdown de configuraciones o herramientas (`fa-screwdriver-wrench`)
- **WHEN** un usuario clica sobre este ícono superior derecho
- **THEN** se despliega una lista clara y actualizada que contenga "Gestión Beneficiarios" y "Gestión Categorías".
- **AND** deben desaparecer viejos enlaces inútiles a rutas inexistentes (ej "Gestión de Entidades" `/entidades` y "Gestión de Cuentas" `/accounts`).

### Requirement: Funcionamiento correcto de Eventos Abiertos
- **GIVEN** los items "Gestión Beneficiarios" y "Gestión Categorías" elegibles desde el dropdown superior
- **WHEN** un usuario interactúa con ellos con click
- **THEN** un evento `window.dispatchEvent` invoca la apertura precisa de la Modal nativa correspondiente
- **AND** el navegador no navega forzadamente hacia rutas vacías (url hash `#` u `onclick` previene la redirección).
