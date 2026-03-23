# Tasks: Standardize Naming to English

## Phase 1: Backend Audit & Refactoring
- [x] **Model Check:** Ensure all models in `models_v2.py` use English field names.
- [x] **API Check:** Ensure all routers in `api/v1/` use English schemas.
- [x] **Transactions API:** Added `start_date` / `end_date` params alongside deprecated `fecha_inicio` / `fecha_fin`.
- [ ] **Retro Layer Update:** Modify `backend/api/retro.py` to stop the re-mapping.

## Phase 2: Frontend JS Standardization
- [x] **Category Manager (`category-manager.js`):** All fields English.
- [x] **Beneficiary Manager (`beneficiary-manager.js`):** All fields English.
- [x] **Transaction Form (`transaction-form.js`):** All fields English.
- [x] **Sidebar Manager (`sidebar-manager.js`):** Removed `nombre_stock`/`nombre_asset` fallbacks.
- [x] **Dashboard JS (`dashboard.js`):** Consistent naming.

## Phase 3: Frontend Template Update
- [x] **`base.html` (sidebar):** All 7 account sections updated (acc.id, acc.name, acc.color).
- [x] **`categories.html`:** Updated Alpine bindings.
- [x] **`accounts.html`:** Updated Alpine bindings.
- [x] **`beneficiaries.html`:** Updated Alpine bindings.
- [x] **`financial_entities.html`:** Updated Alpine bindings.
- [x] **`tags.html`:** Updated Alpine bindings.
- [x] **`transactions.html`:** Updated Alpine bindings.
- [x] **`modals/category_manager.html`:** Updated input bindings.
- [x] **`recurring.html`:** Updated bindings.
- [x] **`budgets.html`:** Updated bindings.
- [x] **`assets.html`:** Updated bindings.
- [x] **`import_csv.html`:** Updated bindings.

## Phase 4: Widget Audit
- [x] **`widget-balance-total.js`:** Clean. Added fallback for `purchase_price`.
- [x] **`widget-monthly-summary.js`:** Added `start_date`/`end_date` alongside legacy params.
- [x] **`widget-recent-transactions.js`:** Clean.
- [x] **`widget-dolar-hoy.js`:** Clean (external API).
- [x] **`widget-ia-insights.js`:** Clean.
- [x] **`widget-quick-add.js`:** Clean.
- [x] **`widget-panel.js`:** Clean.
- [x] **`dashboard.js`:** Clean.

## Phase 5: Remaining Template Fixes
- [x] **`stocks.html`:** Fully standardized (name, symbol, type, quantity, buy_price, current_price, commission, is_active, notes, account_id). Changed API from `cuentas/` to `accounts/`.
- [x] **`goals.html`:** Fully standardized (name, target_amount, current_amount, target_date, account_id). Aligned with backend GoalCreate/GoalUpdate schemas.
- [x] **`forecasting.html`:** Updated dropdown to use `acc.id`/`acc.name`. Changed API from `cuentas/` to `accounts/`. Added `account_id` URL param support.
- [ ] **`plugins.html`:** Uses `nombre_tecnico`, `nombre_display` — tied to backend Plugin model. Deferred until backend model migration.
- [ ] **`vault.html`:** Uses `nombre_tecnico` for plugin check — same dependency as plugins.html.

## Phase 6: Final Verification
- [ ] Audit all remaining `.js` and `.html` files for traces of `nombre`, `id_`, `monto_`, etc.
- [ ] Test all CRUD operations end-to-end.
- [ ] Verify UI labels via `i18n.js` remain correct.


