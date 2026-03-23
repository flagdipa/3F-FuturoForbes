# Design: Verificación E2E Automatizada

## Architecture

1. **Framework de Pruebas:** Utilización de Playwright (instalado en el proyecto) para orquestar la navegación y las aserciones sobre el DOM y red.
2. **Metodología de "Agentes/Scenarios":** Cada bloque lógico (autenticación, entidades, transacciones) se tratará como un conjunto de tareas secuenciales. Una tarea fallida no debe detener por completo la recolección, usando `test.soft()` o captura de excepciones tolerante.
3. **Mapeo de Rutas (Fases):**
   - **Autenticación**: `/register`, `/login`, flujos en layout dashboard.
   - **Configuraciones/Entidades**: `/accounts`, `/payees`, `/categories` (CRUD en interfaz).
   - **Operativa Core**: `/transactions` (incluyendo validación del formulario OCR si aplica o split), `/budgets`, `/goals`.
4. **Mecanismo de Recolección de Errores**: Todo crash en la UI (errores de AlpineJS en consola), promesas del Backend (4xx/5xx HTTP Status Codes) o flujos no esperados, serán interceptados programáticamente y exportados a un reporte final.

## Data Model

No hay alteraciones a los esquemas de la base de datos de producción/desarrollo. La ejecución se realizará apuntando al servidor de desarrollo (SQLite local, puerto 8000).

## Components / Entregables

1. **`frontend/tests/full_e2e_agent.spec.js`**: Script único de Playwright u organizado en suites enfocadas al testing exhaustivo horizontal.
2. **`error_report.md`**: Artefacto final generado por el log de fallos, con el detalle del endpoint / pantalla donde ocurrió la deficiencia detectada.
