# Proposal: Seed Demo Data

## Problem

El sistema 3F no tiene datos de ejemplo concretos para pruebas de desarrollo. Esto obliga a crear registros manualmente cada vez que se reinicia el entorno, lo que ralentiza el proceso de desarrollo, verificación de bugs y testing de la UI.

Además, hasta ahora las pruebas se ejecutan contra una base de datos vacía, lo que no refleja el comportamiento real del sistema con datos reales (por ejemplo, no es posible verificar correctamente los filtros de transacciones, los gráficos del dashboard, o los presupuestos sin datos reales).

## Proposed Solution

Crear un script de **seed de datos de demostración** que:

1. **Importe un set de datos realistas** directamente a la base de datos SQLite local del sistema (o PostgreSQL si aplica), representando un año fiscal de actividad financiera de un usuario ficticio.
2. **Sea idempotente** — se puede ejecutar múltiples veces sin duplicar datos (utiliza `upsert` o verifica existencia previa).
3. **Esté integrado al flujo de desarrollo** — ejecutable con un comando simple (`python -m backend.scripts.seed_demo`).
4. Los datos generados cubrirán:
   - 1 usuario de prueba con credenciales conocidas
   - 5-10 cuentas (banco, efectivo, tarjeta, plazo fijo, etc.)
   - 10-20 categorías (gastos, ingresos, sub-categorías)
   - 10-15 beneficiarios
   - 200-500 transacciones distribuidas en los últimos 12 meses
   - 3-5 presupuestos activos con líneas de categorías
   - 2-3 etiquetas (tags)
   - 2-3 transacciones programadas (recurring)

## Impact

- **backend/scripts/seed_demo.py**: Script principal de seed
- **backend/scripts/clear_demo.py**: Script auxiliar para limpiar datos de demo
- **backend/database/demo_fixtures/**: Carpeta con datos base en JSON, fácil de editar
- **Ningún modelo de datos nuevo** — se usa la estructura existente

## Why Now

Sin datos de prueba concretos y consistentes, es imposible validar correctamente los fixes del sistema (como el que acabamos de aplicar para el Libro de Transacciones). Cada ciclo de testing requiere crear datos manuales, introduciendo variabilidad y perdiendo tiempo crítico.
