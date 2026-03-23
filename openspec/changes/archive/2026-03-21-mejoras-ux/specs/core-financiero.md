# Especificación Delta: Core Financiero (UX/Entidades)

## Capabilities

Esta actualización define mejoras sustanciales en cómo se presentan y organizan las cuentas y bancos:

1. **Entidades Financieras (Institutions):**
   - Deben poseer una ventana y CRUD idéntico a nivel de usabilidad al existente para *Categorías*.
   - El usuario debe poder crear Entidades asignándoles un **Ícono** visual (Ej. ícono de banco, billetera, crypto). 
   - La selección de este ícono aparecerá al lado del campo de "Tipo de entidad" en la ventana de creación/edición.

2. **Vinculación a Cuentas:**
   - A nivel funcional, las `Accounts` (Cuentas) deben poder pertenecer o estar explícitamente asociadas a estas Entidades Financieras previamente cargadas en el sistema. (Uso de `institution_id`).

3. **Visualización de Cuentas (Ledger Style):**
   - Se abandona la visualización básica / cards para la lista general de Cuentas. 
   - Las cuentas deben listarse en una **Tabla Tabular** (parecida estructuralmente al libro de transacciones o el ledger), ofreciendo vistas rápidas de columnas como: Entidad (con su ícono), Nombre, Tipo, Moneda, y Saldo.
