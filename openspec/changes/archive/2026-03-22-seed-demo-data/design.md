# Design: Seed Demo Data

## Architecture

El seed utiliza directamente los modelos SQLModel existentes (sin ORM personalizado) para garantizar que los datos respetan las mismas validaciones que el backend real.

```
backend/
├── scripts/
│   ├── seed_demo.py          ← Script principal
│   └── clear_demo.py         ← Limpia registros de demo
└── database/
    └── demo_fixtures/
        ├── accounts.json
        ├── categories.json
        ├── payees.json
        └── transactions.json  ← generados dinámicamente para el seed
```

## Execution Flow

```
python -m backend.scripts.seed_demo
        │
        ├──▶ 1. Conecta DB (usa misma config que el backend)
        ├──▶ 2. Crea usuario demo (demo@3f.local / demo123)
        ├──▶ 3. Seed currencies (ARS, USD)
        ├──▶ 4. Seed accounts (5-10 cuentas variadas)
        ├──▶ 5. Seed categories (árbol jerárquico gastos/ingresos)
        ├──▶ 6. Seed payees (10 beneficiarios)
        ├──▶ 7. Seed tags (3 etiquetas)
        ├──▶ 8. Seed transactions (300 tx en últimos 12 meses)
        │       └── usa random con seed fijo para reproducibilidad
        ├──▶ 9. Seed recurring (3 programadas: alquiler, sueldo, Netflix)
        └──▶ 10. Seed budgets (presupuesto mensual con líneas por cat.)
```

## Key Design Decisions

### Idempotencia
El script verifica existencia del usuario demo antes de crear. Si ya existe, pregunta `--force` para resetear o sale sin hacer nada. Esto garantiza que se puede correr en CI o en dev sin romper datos existentes.

### Datos Realistas
- Transacciones con montos en rangos reales (ARS y USD)
- Distribución realista: 70% gastos, 30% ingresos
- Nombres de beneficiarios reales: "Coto Digital", "MercadoPago", "Rapipago", "BCRA", etc.
- Fechas aleatorias pero con `random.seed(42)` para reproducibilidad

### Integración con el Sistema
- Se importa `get_db()` y `LedgerEngine` igual que los endpoints reales
- Los balances de cuenta se actualizan correctamente via `LedgerEngine`
- Compatible con SQLite (dev) y PostgreSQL (producción)

## Clear Script

`clear_demo.py` elimina solo los registros del usuario `demo@3f.local`, dejando intactos los datos reales de otros usuarios. Útil para resetear el entorno sin borrar la base de datos completa.
