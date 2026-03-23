# Tasks: System Stabilization V2

## 1. Frontend: Script Architecture (Refactor)

- [ ] **1.1 Update `base.html`**: Mover todos los scripts de lógica de negocio (managers, stores e i18n) a la cabecera (`<head>`) utilizando el atributo `defer`.
- [ ] **1.2 Finalize Alpine.js loading**: Posicionar la librería `Alpine.js` al final del documento (justo antes de `</body>`) también con `defer` para un arranque determinístico.
- [ ] **1.3 Cache-Busting**: Aplicar el sufijo `?v=force_v10` a todos los scripts locales para forzar la recarga del navegador tras la reestructuración.

## 2. Frontend: Transactions Module (Repair)

- [ ] **2.1 Audit `transactions.html`**: Restaurar las funciones de interacción `newTransaction()`, `editTransaction()`, `applyFilters()` y `loadMore()`.
- [ ] **2.2 Scope Verification**: Asegurar que las dependencias de `$store` y los helpers de moneda (`formatCurrency`) estén correctamente vinculados al componente de página.
- [ ] **2.3 Debug Logs**: Inyectar trazas de consola en el cierre del componente Alpine para verificar el éxito de la inyección de datos.

## 3. Backend: Recurring Transactions API

- [ ] **3.1 Model Verification**: Revisar que el modelo `RecurringTransaction` esté presente en `backend/models/models_v2.py` y sea compatible con SQLModel.
- [ ] **3.2 Create Router**: Implementar `backend/api/v1/recurring.py` con los endpoints básicos de listado y creación.
- [ ] **3.3 Router Registration**: Incluir el módulo de recurrencias en el `api_router` principal de la V1.

## 4. Internationalization & UI Polish

- [ ] **4.1 Language Sync**: Auditar los archivos de traducción y añadir las claves faltantes (`nav.currencies`, `nav.vault`, `common.all`).
- [ ] **4.2 User Profile Sync**: Verificar que el nombre del usuario se inyecte dinámicamente en el encabezado.

## 5. End-to-End Validation

- [ ] **5.1 Automated Browser Check**: Utilizar el subagente para verificar el flujo completo y confirmar que los errores de consola han desaparecido.
