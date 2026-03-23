# Proposal: Validación General End-to-End del Sistema

## Problem Context
Tras una serie de refactorizaciones profundas para saldar deuda técnica (actualización de modelos V2, corrección de rutas de API, restauración de la suite de tests y cambio de motor de OCR), el backend ha alcanzado un estado de estabilidad teórica (15/15 tests passing). Sin embargo, es imperativo validar que el frontend sigue sincronizado con estos cambios y que la experiencia de usuario (UX) no se ha degradado por cambios en los esquemas de datos o endpoints.

## Proposed Solution
Realizar una auditoría completa de funcionalidades a través de la interfaz de usuario (UI) utilizando el navegador. El proceso incluirá:
1.  **Flujo Crítico**: Registro -> Login -> Configuración inicial (Monedas/Cuentas).
2.  **Operativa Diaria**: Creación de transacciones (manual y vía OCR), gestión de beneficiarios y categorías.
3.  **Planificación**: Configuración de presupuestos y metas de ahorro (validando los nuevos modelos de datos).
4.  **Reportes e IA**: Verificación de carga de gráficos, insights y forecasting.

Durante este proceso, se generará un log detallado de inconsistencias visuales, errores de consola (404/500) o fallos de lógica.

## Impact
- **Confianza**: Garantía de que los cambios en el core no rompieron la funcionalidad visual.
- **Calidad**: Identificación de bugs "de último minuto" antes de dar el sistema por estabilizado.
- **Documentación**: Lista actualizada de errores conocidos para su posterior corrección rápida.
