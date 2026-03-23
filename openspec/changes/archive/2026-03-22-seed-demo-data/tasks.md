# Tasks: Seed Demo Data

## 1. Estructura de directorios y fixtures
- [x] 1.1 Crear carpeta `backend/database/demo_fixtures/`
- [x] 1.2 Crear `backend/database/demo_fixtures/accounts.json` con 8 cuentas: banco ARS, banco USD, tarjeta crédito, efectivo ARS, efectivo USD, plazo fijo, cuenta inversiones, billetera virtual.
- [x] 1.3 Crear `backend/database/demo_fixtures/categories.json` con árbol de categorías completo (Ingresos: Salario, Freelance, Dividendos; Gastos: Alimentación, Transporte, Servicios, Entretenimiento, Salud, Educación, Alquiler)
- [x] 1.4 Crear `backend/database/demo_fixtures/payees.json` con 12 beneficiarios (Coto, MercadoPago, HSBC, Apple, Netflix, Personal, YPF, etc.)

## 2. Script principal `seed_demo.py`
- [x] 2.1 Crear `backend/scripts/__init__.py` si no existe
- [x] 2.2 Crear `backend/scripts/seed_demo.py` con:
  - Argparse para `--force` flag
  - Conexión a DB usando `get_db()` del sistema
  - Lógica de verificación de usuario demo existente
  - Funciones: `seed_currencies()`, `seed_user()`, `seed_accounts()`, `seed_categories()`, `seed_payees()`, `seed_tags()`, `seed_transactions()`, `seed_recurring()`, `seed_budgets()`
  - `random.seed(42)` para reproducibilidad en transacciones
  - Inserción de 300 transacciones en los últimos 12 meses via LedgerEngine
  - Logs de progreso con `print` / `rich` si disponible

## 3. Script de limpieza `clear_demo.py`
- [x] 3.1 Crear `backend/scripts/clear_demo.py` que:
  - Identifica el usuario `demo@3f.local`
  - Elimina en orden seguro: splits → tags_links → transactions → budgets → payees → categories → accounts → tags → user
  - Imprime confirmación

## 4. Verificación
- [x] 4.1 Ejecutar `python -m backend.scripts.seed_demo` y verificar salida sin errores
- [x] 4.2 Verificar en el browser que el Libro de Transacciones del usuario demo carga al menos 200 registros (Verificado por script)
- [x] 4.3 Verificar que `python -m backend.scripts.seed_demo` (segunda ejecución) no duplica datos
- [x] 4.4 Verificar que `python -m backend.scripts.clear_demo` limpia solo el usuario demo
