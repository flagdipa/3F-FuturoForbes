## Why

El cambio anterior (`unificar-documentacion-openspec`) resultó en la consolidación exitosa de la Fase 1 (Core Financiero, Seguridad y Plugins base). Para lograr una cobertura completa de las mecánicas financieras del sistema 3F, es mandatorio proseguir con la **Fase 2 (Gestión Avanzada)**. 

Esto asegurará que mecánicas más complejas e independientes (presupuestos, metas, activos e inversiones físicas/digitales y recurrencia) estén representadas formalmente bajo el estándar OpenSpec.

## What Changes

- **Consolidación de Gestión Avanzada**: Mapeo completo de las capacidades no críticas pero fundamentales para el producto final, usando la misma estrategia de "Escalpelo Vertical" sobre los relevamientos originales.
- **Creación de Specs**: 
  - `gestion-presupuestos.md`
  - `metas-ahorro.md`
  - `activos-inversiones.md`
  - `transacciones-recurrentes.md`

## Capabilities

### New Capabilities
- `gestion-presupuestos`: Reglas de negocio profundas sobre alertas y presupuestos (mensual, rolling, anual).
- `metas-ahorro`: Tracking visual y aportes (`/goals`).
- `activos-inversiones`: Gestión paralela de bienes físicos depreciables (`/assets`) y activos financieros (`/stocks`).
- `transacciones-recurrentes`: Motor de calendarización transversal para transacciones.

### Modified Capabilities
- *Ninguna*

## Impact

- **Documentación**: Enriquecimiento del directorio base de OpenSpec.
- **Preparación para IA y Futuro**: Estas specs sirven como "knowledge base" para el desarrollo o testing futuro que aplique a la lógica de inversiones y presupuestos.
- **No impacta código**: Seguimos puramente en etapa de redacción y migración documental.
