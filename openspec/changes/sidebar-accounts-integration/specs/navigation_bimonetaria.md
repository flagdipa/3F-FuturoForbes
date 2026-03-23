# Spec: Integración de Cuentas en Sidebar y Navegación Bimonetaria

## ADDED Requirements

### Requirement: Navegación de Transacciones Dividida por Moneda
El sidebar debe presentar dos accesos distintos para transacciones, uno para Pesos (ARS) y otro para Dólares (USD).

#### Scenario: Selección de Moneda ARS
- **GIVEN** El usuario está en el dashboard
- **WHEN** Hace clic en "Transacciones Pesos" en el sidebar
- **THEN** Se abre la vista de transacciones
- **AND** El filtro de moneda se activa automáticamente en ARS
- **AND** El sidebar muestra únicamente las cuentas en Pesos

---

### Requirement: Listado de Cuentas Reactivo en Sidebar
El sidebar debe mostrar un listado dinámico de las cuentas del usuario, filtrado por la moneda activa del contexto de navegación.

#### Scenario: Filtrado de Cuentas por Dólares
- **GIVEN** El usuario hace clic en "Transacciones Dólares"
- **WHEN** Observa la sección de cuentas en el sidebar
- **THEN** Ve cuentas como "Ahorro USD", "Binance USDT", etc.
- **AND** Ve el saldo actualizado de cada una al lado del nombre

---

### Requirement: Filtrado de Transacciones por Cuenta desde Sidebar
Al hacer clic en una cuenta específica dentro del sidebar, la vista de transacciones debe actualizarse para mostrar solo los movimientos de esa cuenta.

#### Scenario: Clic en Cuenta Específica
- **GIVEN** El usuario ve el listado de cuentas ARS en el sidebar
- **WHEN** Hace clic en "Banco Galicia ARS"
- **THEN** La tabla de transacciones se filtra para mostrar solo las del ID de esa cuenta.
