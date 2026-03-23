## Why
El usuario requiere una serie de mejoras fuertes en la Experiencia de Usuario (UX) a lo largo de toda la plataforma, apuntando a una usabilidad más profesional inspirada en MoneyManagerEX. Existen fricciones en cómo se visualizan las cuentas, cómo se operan las transacciones recurrentes (falta un calendario visual) y cómo se configura el layout del dashboard.

## What Changes
1. **Sidebar / Layout**: La barra lateral se colapsa a nivel de íconos en lugar de desaparecer por completo. 
2. **Centro de Control**: Personalización robusta de widgets con selectores (checkboxes) y soporte responsivo libre.
3. **Core Financiero**:
   - Ventana dedicada para "Entidades Financieras" estilo gestor de categorías (con íconos).
   - Linking explícito Cuentas -> Entidades.
   - Vista de tabla tabular (ledger-style) para el listado de cuentas.
4. **Transacciones Recurrentes**: Inclusión de un calendario interactivo para visualizar, crear o repautar eventos recurrentes al hacer clic en ellos (estilo MMEX).

## Capabilities
- `temas-customizacion`: Navbar/Sidebar states, Grid layout builder.
- `core-financiero`: UI de Cuentas y Entidades Financieras.
- `transacciones-recurrentes`: Calendar View & Modal Crud.

## Impact
- **Frontend (Alpine + AdminLTE)**: Alta cantidad de cambios de UI (GridStack checkboxes, FullCalendar para las recurrentes, layout de tabla para cuentas).
- **Backend (FastAPI)**: Posiblemente nuevos endpoints CRUD formales para `institutions` (Entidades financieras) si no estaban expuestos totalmente.
