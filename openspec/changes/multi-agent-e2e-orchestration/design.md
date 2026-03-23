# Design: Arquitectura de Verificación E2E Multi-Agente

## Architecture
1. **Agente Orquestador (Master)**: Se encarga de la configuración del entorno general (servidor base up) y asigna las secciones a probar a los Workers. Al finalizar la auditoría, lee la información generada por todos en `worker_report_*.md` y crea el `master_bug_report.md`.
2. **Agentes Workers (Roles Asignados)**: 
   - **Worker A (Auth)**: Valida Registro, Login y manejo de Sesiones JWT.
   - **Worker B (Entidades)**: Valida el CRUD completo local de Accounts, Categorías y Beneficiarios.
   - **Worker C (Transacciones)**: Audita la tabla de Transacciones, splits, y el subidor OCR.
   - **Worker D (Tools)**: Verifica gráficas de Insights, Presupuestos y Metas.

## Mecanismos de Sincronización (File-based IPC)
- Al no haber chat entre agentes, la comunicación y orquestación ocurre a través del bloqueo y completado de las tareas en formato Markdown: `tasks.md`.
- Cada modelo (Worker) se encargará exclusivamente de las tareas que el Orquestador le haya delegado, subiendo sus hallazgos en un archivo aislado para no escribir al mismo tiempo en un archivo compartido (evitando colisiones en disco).
- El Orquestador finalmente ejecuta un comando de concatenación o lee los reportes mediante herramientas de análisis y formula los tickets de corrección.

## Entregables
- Scripts paralelizables alojados en `frontend/tests/workers/`.
- Un documento maestro de bugs, categorizando si el error pertenece al Backend (Network request error), al Frontend JS (Alpine error), o es una deflexión de la UI.
