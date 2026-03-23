# Proposal: Refactor de Navegación e Interacciones UI/UX

## What

Este cambio se enfoca en mejorar la usabilidad y la consistencia visual del sistema 3F mediante cuatro intervenciones clave:
1. **Unificación de Botones:** Alinear y estandarizar el tamaño de los botones de acción en la parte inferior de las vistas (ej. Nueva Transacción, Editar, Duplicar, Eliminar).
2. **Interacción de Tabla:** Implementar el evento de doble clic en las filas de la tabla de transacciones para abrir el modal de edición, permitiendo una navegación más fluida.
3. **Reorganización del Sidebar:** Eliminar los accesos directos de "Beneficiarios" y "Categorías" del sidebar (Catálogos) para reducir el ruido visual en la barra lateral.
4. **Refactor del Menú Superior:** Transformar el actual menú de "Herramientas" en un centro de gestión de "Entidades y Cuentas", integrando allí los accesos a Beneficiarios y Categorías.

## Why

* **Consistencia Visual:** Los botones de diferentes tamaños rompen la armonía del diseño "Neon" y dificultan la interacción rápida.
* **Eficiencia del Usuario (UX):** El doble clic es un patrón estándar en aplicaciones de gestión para editar registros. Actualmente, el sistema requiere seleccionar y luego hacer clic en un botón separado.
* **Arquitectura de Información:** El sidebar debe reservarse para la navegación de alto nivel (Dashboard, Transacciones, Reportes). La gestión de entidades maestras (Beneficiarios, Categorías) es más apropiada dentro de un menú de herramientas o configuración.
* **Semántica:** El término "Herramientas" es muy genérico; "Gestión de Entidades" o similar es más descriptivo para las tareas de mantenimiento de datos maestros.

## Impact

* **Frontend (HTML/JS):** Cambios en `base.html` para la estructura del menú y sidebar. Actualización de `neon-3f.css` para la alineación de botones.
* **Interacciones (Alpine.js):** Modificación del componente de tabla en `transactions/index.html` (o `main.js`) para capturar el evento `@dblclick`.
* **Experiencia de Usuario:** Mejora inmediata en la "fricción" de uso diario del sistema.
