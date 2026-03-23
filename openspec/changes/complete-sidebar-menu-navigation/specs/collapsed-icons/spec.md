## ADDED Requirements

### Requirement: Iconos visibles en sidebar colapsado
Cuando el sidebar está en modo colapsado (mini sidebar), los iconos de FontAwesome deben ser claramente visibles y centrados en cada item de navegación.

#### Scenario: Visualización de iconos en modo colapsado
- **WHEN** el sidebar está colapsado (clase `sidebar-collapse` en body)
- **THEN** los iconos `.nav-icon` deben tener:
  - `display: flex` con centrado horizontal y vertical
  - `font-size: 1.2rem` para ser claramente visibles
  - `width: 28px` y `height: 28px` para área de clic adecuada
  - `margin-right: 0` para centrado completo
  - Color de texto visible (heredar o aplicar color específico)

#### Scenario: Iconos mantienen color temático
- **WHEN** el sidebar está colapsado
- **THEN** cada icono debe mantener su color temático asignado (text-primary, text-success, etc.)
- **AND** el color debe ser suficientemente contrastante con el fondo oscuro

#### Scenario: Tooltips en hover
- **WHEN** el usuario pasa el cursor sobre un icono en modo colapsado
- **THEN** debe aparecer un tooltip con el texto del item (usando el atributo `data-label`)
- **AND** el tooltip debe posicionarse a la derecha del icono
- **AND** debe desaparecer al quitar el cursor

### Requirement: Items colapsados mantienen funcionalidad
Los items de navegación deben seguir siendo clicables y funcionales cuando el sidebar está colapsado.

#### Scenario: Clic funcional en modo colapsado
- **WHEN** el usuario hace clic en un icono del sidebar colapsado
- **THEN** debe navegar a la URL correspondiente
- **AND** no debe haber áreas de clic invisibles o solapadas
