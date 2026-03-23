# Proposal: E2E Tests para Auth y Cuentas (Worker 1)

## What
Implementar estricta y funcionalmente las tareas de la "Fase 1" heredadas de la propuesta `multi-agent-e2e-orchestration`. Específicamente, se construirán los scripts de Playwright `worker_1_auth.spec.js` (para validar el login y registro de sistema) y `worker_1_accounts.spec.js` (para inspeccionar vistas y creación de cuentas bancarias). Seguido de esto, el sistema atrapará todos los `console.error` o códigos de estado `500` en un archivo `worker_1_report.md`.

## Why
Es necesario delegar el diseño completo de pruebas por módulos. Puesto que las ramas de Categorías, Transacciones y Split ya fueron testeadas en paralelo (creando instancias del Worker 2 y 3), nos falta garantizar que la capa de Entrada (Login) y de gestión central (Cuentas) no estén arrojando bugs de AlpineJS ni bloqueos de Backend.

## Impact
- **Cobertura**: Asegura un flujo de sesión robusto (JWT validation indirecta) antes de iterar transacciones.
- **Reporting**: Nutrirá de métricas reales al Orquestador cuando se vuelva a invocar el resumen final.
