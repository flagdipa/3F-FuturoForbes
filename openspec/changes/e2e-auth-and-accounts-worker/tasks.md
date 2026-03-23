# Tasks: Pruebas Exhaustivas de Worker 1 (Fase 1)

## Bloque Autenticación
- [x] 1.1 Crear `frontend/tests/workers/worker_1_auth.spec.js` programando los tests de Playwright para ingresar a `/login` tanto con credenciales nulas/inválidas como correctas, incluyendo `/register`.

## Bloque Vistas (Cuentas)
- [x] 2.1 Crear `frontend/tests/workers/worker_1_accounts.spec.js`, asumiendo login previo, navegando a `/accounts`.
- [x] 2.2 Programar la intercepción de fallos de red (`>= 400`) y de consola de Alpine JS a través del evento `console` del "Page" obj.

## Bloque Verificador y Reporte (The Worker Runner)
- [x] 3.1 Abrir terminal sobre la raíz local apuntando a `frontend/` y ejecutar la CLI de Playwright únicamente con ambos scripts (por ej. `npx playwright test worker_1_`).
- [x] 3.2 Imprimir el log unificado final en `c:\xampp\htdocs\3F\openspec\changes\e2e-auth-and-accounts-worker\worker_1_report.md` y documentar si aparecen de nuevo bloqueos en `sidebar` o `fetch` errors.
