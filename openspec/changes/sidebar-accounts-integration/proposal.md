# Proposal: Integración de Cuentas en el Sidebar

## What

Este cambio propone integrar el listado de cuentas bancarias y de activos directamente en el Sidebar, con un enfoque bimonetario. El menú de "Transacciones" se dividirá en "Transacciones en Pesos" y "Transacciones en Dólares". Las cuentas en el sidebar se filtrarán automáticamente según la moneda seleccionada en el menú de navegación superior.

## Why

Actualmente, para filtrar transacciones por cuenta, el usuario debe usar un selector pequeño dentro de la vista de transacciones. Integrar las cuentas en el sidebar:
1.  **Mejora la visibilidad bimonetaria:** El usuario puede alternar rápidamente entre sus finanzas en ARS y USD.
2.  **Agiliza el flujo:** Permite saltar entre contextos contables con un solo clic, filtrando tanto transacciones como cuentas relevantes a la moneda elegida.
3.  **Refuerza el concepto de "Navegación por Entidad":** Alinea el sistema con estándares de software financiero moderno.

## Impact

*   **UI/UX:** El sidebar tendrá un nuevo bloque dinámico (probablemente bajo "Transacciones") con el listado de cuentas.
*   **Comportamiento:** Se implementará un evento global o comunicación entre componentes (Alpine Stores) para que el componente de Transacciones reaccione al clic en el sidebar.
*   **Modales:** Mantendrá la capacidad de abrir la "Gestión de Cuentas" completa desde el nuevo menú superior de Entidades.
