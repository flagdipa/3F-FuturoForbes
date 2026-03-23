# Tasks for unificar-documentacion-openspec

## Fase 1: Specs Críticas

- [x] **1. Crear Spec: core-financiero**
  - **Ubicación:** `openspec/changes/unificar-documentacion-openspec/specs/core-financiero.md`
  - **Instrucciones de Extracción (Escalpelo Vertical):**
    - **Lógica de Negocio:** Leer de `INFORME_RELEVAMIENTO_3F.md` la sección 4.1 (Cuentas, Transacciones, Categorías, Beneficiarios, Presupuestos).
    - **Estructura de Datos:** Leer de `INFORME_RELEVAMIENTO_3F.md` la sección 5.1 (Modelos User, Account, Transaction, Category, Budget).
    - **Endpoints:** Leer de `INFORME_RELEVAMIENTO_3F.md` la sección 6.1 (Auth, /accounts, /transactions, /categories, /budgets).
    - **Acción:** Consolidar estos 3 cortes verticales en la estructura estándar de OpenSpec (Capabilities, Data Models, API Endpoints, Scenarios).

- [x] **2. Crear Spec: sistema-plugins**
  - **Ubicación:** `openspec/changes/unificar-documentacion-openspec/specs/sistema-plugins.md`
  - **Instrucciones de Extracción (Escalpelo Híbrido):**
    - **Arquitectura Base:** Extraer de `PROMPT_PLUGINS.md` la tabla de hooks, el funcionamiento de `PluginManager` y `BasePlugin`, y del `INFORME_RELEVAMIENTO_3F` la sección 4.5.4 y 6.1 (/plugins).
    - **Plugins Simples:** Identificar los plugins menos complejos en `backend/plugins/` (como `telegram_bot`, `email_smtp`, `dolar_hoy`) e incluir sus configuraciones y comportamientos esperados dentro de esta misma spec general.
    - **Acción:** Elaborar una especificación que defina extensibilidad sin tocar el core. *(Nota: Los plugins complejos como `criptoya_multi` se abordarán después, en specs dedicadas).*

- [x] **3. Crear Spec: seguridad-auditoria**
  - **Ubicación:** `openspec/changes/unificar-documentacion-openspec/specs/seguridad-auditoria.md`
  - **Instrucciones de Extracción (Escalpelo Vertical):**
    - **Lógica de Negocio:** Leer de `INFORME_RELEVAMIENTO_3F.md` la sección 4.5.2 (Auditoría completa) y repasar la sección técnica 3.1 sobre Seguridad (JWT/SlowAPI).
    - **Estructura de Datos:** Leer de `INFORME_RELEVAMIENTO_3F.md` las secciones correspondientes al la tabla `User` (5.1.1) y la tabla de auditoría inmutable `AuditLog` (5.1.10).
    - **Endpoints:** Leer de `INFORME_RELEVAMIENTO_3F.md` los fragmentos de la API sobre `/auth` y `/audit` (sección 6.1).
    - **Acción:** Escribir la especificación centralizando flujos de autenticación, rate limiting y registro inmutable de transacciones.

*(Las Fases 2, 3 y 4 se definirán e iterarán sobre las 11 specs restantes una vez que completemos y validemos la mecánica de la Fase 1).*
