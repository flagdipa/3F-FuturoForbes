# Specs: Corrección de Sincronización entre Capas

## ADDED Requirements

### Requirement: Todas las rutas del menú sidebar deben responder con HTTP 200

Todas las URLs referenciadas en `base.html` deben tener una ruta correspondiente en `ui_router.py` que devuelva el template correcto.

#### Scenario: Navegación a Configuración
- **GIVEN** El usuario está logueado y en cualquier página del sistema
- **WHEN** Hace clic en "Configuración" en el sidebar (`/configuracion`)
- **THEN** El sistema muestra la página de configuración (`settings.html`) sin error 404

#### Scenario: Navegación a Cuentas
- **GIVEN** El usuario está logueado
- **WHEN** Hace clic en "Listado" dentro de "Gestión Cuentas" (`/cuentas`)
- **THEN** El sistema muestra la vista de cuentas (`accounts/index.html`)

#### Scenario: Navegación a Presupuestos
- **GIVEN** El usuario está logueado
- **WHEN** Hace clic en "Presupuestos" (`/presupuestos`)
- **THEN** El sistema muestra la vista de presupuestos (`budgets/index.html`)

#### Scenario: Navegación a sub-rutas de Reportes y Mercado
- **GIVEN** El usuario está logueado
- **WHEN** Hace clic en "Cashflow" (`/reportes/cashflow`), "Heatmap" (`/reportes/heatmap`), "Dólar Hoy" (`/mercado/dolar`), o "Crypto" (`/mercado/crypto`)
- **THEN** Se muestra el template correspondiente sin error 404

---

### Requirement: El sidebar colapsado debe mostrar iconos en desktop

En pantallas >= 992px, al colapsar el sidebar, debe mantenerse visible como mini-sidebar de ~54px mostrando solo los iconos de navegación.

#### Scenario: Colapsar sidebar en desktop
- **GIVEN** El usuario está en una pantalla >= 992px con sidebar expandido
- **WHEN** Hace clic en el botón de toggle del sidebar
- **THEN** El sidebar se reduce a ~54px, mostrando solo los iconos centrados
- **AND** Al hacer hover sobre un ícono, se muestra un tooltip con el nombre de la sección

#### Scenario: Sidebar en móvil
- **GIVEN** El usuario está en pantalla < 992px
- **WHEN** El sidebar está cerrado
- **THEN** No se ve ningún sidebar (comportamiento drawer off-canvas, no mini-sidebar)

---

### Requirement: Los headers de la tabla de transacciones muestran texto traducido

#### Scenario: Visualización de columnas con i18n
- **GIVEN** El usuario está en la página de transacciones
- **WHEN** La tabla se renderiza
- **THEN** Cada columna muestra su nombre traducido ("TIPO", "FECHA", "HORA", "CUENTA", "BENEFICIARIO", "CATEGORÍA", "MONTO", "SALDO", "ETIQUETAS", "ESTADO") en lugar de los paths crudos del i18n

---

### Requirement: Menú sidebar debe incluir accesos a Catálogos

#### Scenario: Acceso a Beneficiarios y Categorías desde sidebar
- **GIVEN** El usuario está en cualquier página del sistema
- **WHEN** Mira el sidebar
- **THEN** Existe una sección "Catálogos" con accesos directos a Beneficiarios y Categorías (abriendo modal o navegando a la vista correspondiente)
