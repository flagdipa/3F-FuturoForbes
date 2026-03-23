# Design: Estabilización de Endpoints y Frontend

## Goals
1. Garantizar que `saving_goals` y `budgets` tengan sus esquemas de base de datos actualizados.
2. Hacer dinámico el nombre de usuario mostrado en el dashboard.
3. Arreglar las claves de traducción faltantes en el sidebar de navegación.
4. Definir las variables Alpine (`editTx`, `isScanningReceipt`, etc.) para evitar errores de consola en Transacciones.

## Technical Approach

### 1. Recreación de DB (Base de Datos)
Para evitar migraciones manuales en SQLite que fallan a veces, eliminaremos el archivo `3f_app.db` para que el método `init_db()` de `core/database.py` la recree basándose en la versión actual de `models_v2.py`.

### 2. Frontend dinámico (Dashboad & Header)
Actualizaremos las plantillas `frontend/templates/dashboard.html` y los fragmentos de header para inyectar correctamente el nombre del usuario logueado en lugar del string estático "Fer21gon".

### 3. Alpine Stores (JS)
Revisaremos `static/js/app.js` y `static/js/transactions.js` para asegurar que las variables faltantes se inicialicen temprano con `Alpine.store(...)` o `document.addEventListener('alpine:init', ...)`.

### 4. Localización (i18n)
Se actualizarán los archivos JSON (`static/locales/es.json`, `en.json`) para incluir las claves:
- `nav.scheduled`
- `nav.vault`
- `nav.plugins`
- `nav.tags`
- `goals.title`
- `budgets.title`
- `common.duplicate`
- `settings.db_management`
