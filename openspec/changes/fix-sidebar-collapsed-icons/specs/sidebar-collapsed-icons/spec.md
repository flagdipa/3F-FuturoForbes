## ADDED Requirements

### Requirement: Sidebar muestra íconos en modo colapsado
El sistema DEBE mostrar los íconos Font Awesome centrados y visibles cuando el sidebar está en modo colapsado (clase `sidebar-collapse` presente).

#### Scenario: Usuario colapsa el sidebar
- **WHEN** el usuario hace clic en el botón de toggle del sidebar
- **THEN** el sidebar se reduce a un ancho de aproximadamente 54-70px
- **AND** los íconos `.nav-icon` deben permanecer visibles
- **AND** los íconos deben estar centrados horizontalmente en el ancho reducido
- **AND** los textos del menú deben ocultarse
- **AND** los submenús (nav-treeview) deben ocultarse

### Requirement: Íconos centrados y dimensionados correctamente
Los íconos DEBEN tener dimensiones consistentes y estar centrados en el contenedor del enlace cuando el sidebar está colapsado.

#### Scenario: Íconos en sidebar colapsado
- **WHEN** el sidebar está en modo colapsado
- **THEN** cada ícono `.nav-icon` DEBE tener un ancho mínimo de 1.1rem
- **AND** el margen derecho DEBE ser 0 (sin espacio para texto)
- **AND** el ícono DEBE estar centrado horizontalmente usando flexbox o text-align
- **AND** el tamaño de fuente DEBE ser consistente (~1.1rem)

### Requirement: Tooltips funcionan en modo colapsado
El sistema DEBE mostrar tooltips con el nombre de la sección al hacer hover sobre los íconos cuando el sidebar está colapsado.

#### Scenario: Hover sobre ícono colapsado
- **WHEN** el usuario posiciona el cursor sobre un ícono en el sidebar colapsado
- **THEN** debe aparecer un tooltip con el texto del atributo `data-label`
- **AND** el tooltip DEBE posicionarse a la derecha del ícono
- **AND** el tooltip DEBE tener fondo oscuro y borde consistente con el tema
- **AND** el tooltip DEBE tener opacidad 0 inicialmente y mostrarse con transición suave

### Requirement: Compatibilidad responsive
El sidebar colapsado DEBE funcionar correctamente tanto en desktop como en dispositivos móviles.

#### Scenario: Vista en desktop
- **WHEN** la pantalla tiene un ancho mayor o igual a 992px
- **AND** el sidebar está colapsado
- **THEN** el sidebar DEBE mantenerse visible como barra mini de ~54-70px
- **AND** el contenido principal DEBE ajustar su margen izquierdo

#### Scenario: Vista en mobile
- **WHEN** la pantalla tiene un ancho menor a 992px
- **AND** el sidebar se colapsa o cierra
- **THEN** el sidebar DEBE ocultarse completamente (off-canvas)
- **AND** al abrirse, DEBE mostrarse como sidebar completo con íconos y texto
- **AND** los íconos en modo mobile expandido DEBEN mostrarse normalmente con su texto

### Requirement: Preservación de funcionalidad expandida
El sistema NO DEBE afectar el comportamiento del sidebar cuando está expandido.

#### Scenario: Sidebar expandido
- **WHEN** el sidebar NO tiene la clase `sidebar-collapse`
- **THEN** los íconos DEBEN mostrarse con su texto correspondiente
- **AND** los submenús DEBEN ser accesibles y visibles
- **AND** el ancho del sidebar DEBE ser de ~250px
- **AND** los márgenes y espaciados DEBEN mantenerse como en el estado actual

