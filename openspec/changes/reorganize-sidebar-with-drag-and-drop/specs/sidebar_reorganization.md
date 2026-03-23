# Specification: Sidebar Reorganization

## Core Requirements

- The sidebar MUST support drag-and-drop reordering of main navigation items using SortableJS or similar.
- The sidebar MUST dynamically group accounts based on their underlying type or metadata (e.g., Banks, Wallets, Credit Cards) instead of a single "Accounts" list.
- The sidebar MUST dynamically list activated plugins under a "Modules" section, utilizing the existing plugin API.
- The user's custom sidebar order MUST be persisted across sessions using backend storage (e.g., User preferences or SystemConfig).
- The top-level base items MUST include: Dashboard, Transacciones programadas, Transacciones $, Transacciones u$s, Presupuestos, Metas, Módulos, Reportes, Comprobantes, Configuración.

## BDD Requirements

### Requirement: Account Grouping in Sidebar
- **GIVEN** a user has active accounts mapped to types like "Bank" and "Wallet"
- **WHEN** the frontend categorizes these accounts on load
- **THEN** the sidebar should display distinct collapsible sections (e.g., "Cuentas bancarias", "Cuentas billeteras") containing the respective accounts.

### Requirement: Plugin Visibility
- **GIVEN** a user has activated a plugin in the system
- **WHEN** the user views the sidebar
- **THEN** the plugin's navigation entry should dynamically appear under the "Módulos" section.

### Requirement: Drag and Drop Persistence
- **GIVEN** an authenticated user with a loaded sidebar
- **WHEN** the user drags an item (e.g., "Reportes") above another item (e.g., "Transacciones $")
- **THEN** the UI should visually update the order
- **AND** the new order must be immediately saved via an API call
- **AND** upon subsequent page reloads, the sidebar must render honoring the new custom order.
