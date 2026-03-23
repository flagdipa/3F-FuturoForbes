# Tareas de Implementación 

A modificar en el código Python de Backend.

- [ ] **1. Migración de Base de Datos**
  - Generar un script de migración (Alembic o un script en `migrations/`) que agregue la columna `code` (string, unique, index) a las tablas `Account` y `Beneficiary`.
  - Asegurar un fallback para registros viejos (rellenar de forma dummy como `ACT<id>` o similar).

- [ ] **2. Modelos ORM y Schemas Pydantic**
  - Modificar `backend/models/xxx.py` para sumar `code` a `Account` y `Beneficiary`.
  - Modificar la clase `Attachment` sumando `original_filename` y modificando semánticamente los archivos.

- [ ] **3. Lógica API (Core Financiero)**
  - Modificar los schemas de Create en `routers` para Cuentas y Beneficiarios, forzando la obligatoriedad del `code`.

- [ ] **4. Lógica de Renombrado en Bóveda API (`/vault` / `/attachments`)**
  - Interceptar el archivo subido en el `POST`.
  - Consultar en BD el `code` correspondiente vinculando el origen/destino.
  - Formatear el string de tiempo (`datetime.now().strftime('%y%m%d_%H%M')`).
  - Escribir en disco/ruta el archivo con el nuevo título y capturar/guardar el path customizado (`directory`).
