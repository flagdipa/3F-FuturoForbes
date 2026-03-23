# Design: System Stabilization V2

## Context

El sistema se encuentra en un estado inestable tras la migración parcial a la V2 (FastAPI + Alpine.js). Las dependencias reactivas (Alpine Stores) fallan por falta de un orden de carga de scripts predecible, y el backend presenta lagunas en la implementación de rutas críticas (Recurrencias).

## Goals / Non-Goals

### Goals
*   **Asegurar** que todos los almacenes Alpine (`$store`) estén registrados antes de que cualquier componente de página intente acceder a ellos.
*   **Restablecer** la funcionalidad del libro de transacciones eliminando errores de "undefined function".
*   **Implementar** el backend para `/programadas` (Recurring) resolviendo errores 500.
*   **Normalizar** las traducciones i18n en toda la interfaz.

### Non-Goals
*   No se pretende rediseñar la interfaz visual (CSS), solo estabilizar la lógica actual.
*   No se implementarán nuevas características de IA fuera de lo ya proyectado para el OCR básico.

## Technical Design

### 1. Script Loading Strategy (Deterministic Order)

Utilizaremos el comportamiento estándar del navegador para la carga de scripts diferidos:

*   **Librerías Síncronas (Head - No Defer)**: `Axios`, `Bootstrap`, `SweetAlert2`. Disponibles de inmediato para cualquier script inline.
*   **Gobernanza de Negocio (Head - Defer)**: `i18n.js`, `main.js`, `beneficiary-manager.js`, `category-manager.js`. Se descargan en paralelo pero se ejecutan **en orden** tras el parseo del DOM.
*   **Framework Reactivo (Body End - Defer)**: `Alpine.js`. Al ser el último script diferido, Alpine se inicializará **después** de que todos los gerentes hayan definido sus dependencias y stores.

### 2. Alpine.js Component Lifecycle

Para las páginas que inyectan scripts dinámicos (como `transactions.html`):
*   Se usará el patrón de registro diferido:
    ```javascript
    function initTransactions() {
        if (!window.Alpine) return;
        Alpine.data('transaccionesPage', () => ({ ... }));
    }
    // Compatible con carga directa o por evento
    if (window.Alpine) initTransactions();
    else document.addEventListener('alpine:init', initTransactions);
    ```

### 3. Backend Implementation (Recurring API)

*   **Router**: `backend/api/v1/recurring.py`.
*   **Models**: Se asegurará que la tabla `recurring_transactions` use `SQLModel` con relaciones a `accounts`, `payees` y `categories`.
*   **Endpoints**:
    *   `GET /`: Listar todas las tareas programadas activas.
    *   `POST /`: Crear nueva recurrencia.
    *   `POST /{id}/execute`: Ejecutar manualmente una recurrencia (generar asiento en libro diario).

## Risks / Trade-offs

*   **Timing Issue**: Algunos navegadores muy antiguos ignoran `defer` en favor de ejecución inmediata. Se mitiga situando Alpine físicamente al final.
*   **Cache Invalidation**: Se usará el sufijo `?v=force_vXX` en las inclusiones de script en `base.html` para forzar la recarga de los archivos corregidos.
