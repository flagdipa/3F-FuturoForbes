## Why

El menú lateral del sistema 3F está incompleto. Actualmente solo muestra Dashboard, Transacciones, Programadas, Vault y Comprobantes, pero carece de accesos directos a funcionalidades clave como Beneficiarios, Categorías, Cuentas, Presupuestos, Metas y otras herramientas del sistema. Además, cuando el sidebar está colapsado, los iconos no se visualizan correctamente debido a la ausencia de los items de navegación correspondientes.

## What Changes

- Agregar items de navegación faltantes en el sidebar de base.html:
  - Cuentas (con submenú: Listado, Reconciliar)
  - Beneficiarios
  - Categorías
  - Presupuestos
  - Metas de Ahorro
  - Reportes (con submenú: Dashboard, Cashflow, Heatmap)
  - Inversiones
  - Mercado (con submenú: Dólar Hoy, Crypto, CriptoYa)
  - Configuración
- Asegurar que los iconos FontAwesome se muestren correctamente cuando el sidebar está colapsado
- Mantener compatibilidad con el sistema de tooltips existente
- Respetar el diseño visual dark theme actual

## Capabilities

### New Capabilities
- `sidebar-navigation-v2`: Sistema de navegación completo del sidebar con menú jerárquico
- `collapsed-icons`: Visualización de iconos en modo sidebar colapsado

### Modified Capabilities
- `ui-base-template`: Modificar base.html para incluir menú completo

## Impact

- **Frontend**: Modificación de `frontend/templates/base.html`
- **CSS**: Posibles ajustes menores en `frontend/static/css/neon-3f.css` para estilos del menú colapsado
- **UX**: Mejora significativa en navegación y accesibilidad de funcionalidades del sistema
