## ADDED Requirements

### Requirement: Menú Herramientas muestra solo ícono
El menú "Herramientas" en la barra superior DEBE mostrar únicamente el ícono `fa-screwdriver-wrench` sin texto.

#### Scenario: Usuario ve el menú superior
- **WHEN** el usuario carga cualquier página
- **THEN** el menú Herramientas DEBE mostrar solo el ícono
- **AND** NO DEBE mostrar el texto "Herramientas"
- **AND** el ícono DEBE tener un atributo `title` para tooltip nativo

### Requirement: Tipos de Entidad se elimina del menú
La opción "Tipos de Financiera" DEBE eliminarse del menú dropdown Herramientas.

#### Scenario: Usuario abre menú Herramientas
- **WHEN** el usuario hace clic en el ícono de Herramientas
- **THEN** el dropdown DEBE mostrar las opciones restantes
- **AND** NO DEBE incluir la opción "Tipos de Financiera"
- **AND** las demás opciones DEBEN permanecer disponibles

### Requirement: Acceso a Tipos desde ventana Entidades
La ventana de gestión de entidades DEBE incluir un ícono/botón para acceder a "Tipos de Entidad".

#### Scenario: Usuario en ventana de entidades
- **WHEN** el usuario está en la ventana de gestión de entidades
- **THEN** DEBE ver un ícono/botón para acceder a Tipos de Entidad
- **AND** al hacer clic, DEBE navegar a `/entidades#tipos`
- **AND** el ícono DEBE tener tooltip descriptivo

### Requirement: Diccionario actualizado
El diccionario español DEBE usar "Entidades" en lugar de "Financieras".

#### Scenario: Traducciones en español
- **WHEN** el sistema carga el diccionario español
- **THEN** `tools_mgmt` DEBE mostrar "Gestión de Entidades"
- **AND** `entity_types` DEBE mostrar "Tipos de Entidad"
- **AND** todas las referencias a "financiera" DEBEN cambiar a "entidad"

