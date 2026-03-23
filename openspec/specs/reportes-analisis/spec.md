# Spec: Reportes y Análisis

## Goal
Centralizar toda la visualización macro del estado financiero del usuario, alimentando interfaces gráficas (Dashboards) basadas en `GridStack` y librerías de componentes (ej. Chart.js).

## Capabilities
1. **Dashboard Widgets:** Componentes agnósticos inyectables desde el backend que mapean Balance General, Flujos de Caja (Bar/Line charts) y Gastos Mensuales (Doughnut).
2. **Reportes Estáticos:** Consultas analíticas pesadas (Heatmaps diarios) procesadas velozmente mediante views de SQLModel y Pandas en background.

## API Endpoints (`/api/v1/reports`)
- `GET /dashboard` - Data maestra para charts del home.
- `GET /cashflow` - Entradas vs Salidas.
- `GET /categories` - Gasto agrupado.
- `GET /trends`
- `GET /heatmap` - Horarios y días de mayor gasto.
- `GET /wealth` - Patrimonio Neto (Activos Físicos + Cuentas + Inversiones).
