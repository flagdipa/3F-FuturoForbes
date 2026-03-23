## ADDED Requirements

### Requirement: Sidebar muestra navegación completa
El sistema DEBE mostrar un menú de navegación completo en el sidebar que incluya todas las funcionalidades principales del sistema organizadas jerárquicamente.

#### Scenario: Visualización del menú completo
- **WHEN** el usuario carga cualquier página del sistema
- **THEN** el sidebar debe mostrar los siguientes items de navegación:
  - Dashboard (icono fa-gauge-high)
  - Transacciones (icono fa-receipt) con submenú: Nueva, Listado, Importar CSV
  - Programadas (icono fa-calendar-check)
  - Cuentas (icono fa-wallet) con submenú: Listado, Reconciliar
  - Beneficiarios (icono fa-users)
  - Categorías (icono fa-tags)
  - Vault (icono fa-vault)
  - Presupuestos (icono fa-chart-pie)
  - Metas (icono fa-bullseye)
  - Reportes (icono fa-chart-line) con submenú: Dashboard, Cashflow, Heatmap
  - Inversiones (icono fa-line-chart)
  - Mercado (icono fa-globe) con submenú: Dólar Hoy, Crypto, CriptoYa
  - Configuración (icono fa-cog)

#### Scenario: Navegación a secciones
- **WHEN** el usuario hace clic en cualquier item del menú
- **THEN** el sistema debe navegar a la URL correspondiente sin errores
- **AND** el item activo debe resaltarse visualmente

#### Scenario: Submenús expandibles
- **WHEN** el usuario hace clic en un item con submenú
- **THEN** el submenú debe expandirse mostrando sus items hijos
- **AND** al hacer clic nuevamente debe colapsarse

### Requirement: Items usan atributo data-label para tooltips
Cada item del menú DEBE incluir el atributo `data-label` con el texto traducido para permitir la visualización de tooltips cuando el sidebar esté colapsado.

#### Scenario: Atributos data-label presentes
- **WHEN** se inspecciona el HTML del sidebar
- **THEN** cada enlace `.nav-link` debe tener el atributo `data-label` con el texto del item
- **AND** el valor debe coincidir con el texto mostrado en el item expandido
