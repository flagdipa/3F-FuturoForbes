# Design: Implementación del Test Worker 1 (Auth y Cuentas)

## Arquitectura de Pruebas
Dado que estas pruebas E2E apuntan a un flujo transaccional en un solo servidor de prueba (`localhost:8000`), el diseño constará de dos scripts atómicos en Playwright.

1. **`worker_1_auth.spec.js`**:
    - Validará `/login` rellenando campos con fallos intencionales (contraseña inválida) y luego con credenciales demo.
    - Validará la página `/register` visualmente.
2. **`worker_1_accounts.spec.js`**:
    - Logueará un usuario estático e interaccionará con `/accounts`.
    - Buscará el componente AlpineJS para renderizar la tabla o las *cards* de cuentas e intentará abrir el modal correspondiente (`"Nueva Cuenta"`).

## Aserciones de Fallo
Copiaremos la misma metodología del Orquestador introducida en los Workers previos:
- Monitorización activa sobre `console` (`msg.type() === 'error'`).
- Monitorización sobre `response` HTTP (`resp.status() >= 400`).

## Entregables
- Scripts aislados en `frontend/tests/workers/`.
- Archivo resultado local unificado como `worker_1_report.md`, que indicará explícitamente cualquier bug (e.g. JWT errors o Alpine `is undefined`).
