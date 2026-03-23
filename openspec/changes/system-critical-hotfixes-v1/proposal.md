# Proposal: System Critical Hotfixes V1

## Problem Context
El sistema experimenta una cascada de fallos persistentes debido a deuda técnica y residuos de implementaciones previas (como la eliminación parcial del motor OCR en línea basado en Gemini IA). Además, los arreglos de interfaz recientes para acomodar herramientas en la barra superior causaron una seria desalineación de capas (glitches de AdminLTE y Bootstrap 5) al omitirse clases maestras (`.dropdown`). Por último, las interacciones Alpine.js - JavaScript nativo quedaron desconectadas (`open-categories` vs `open-category-manager`), inutilizando botones que el usuario utiliza diariamente para ingresar categorías y beneficiarios.

## Proposed Solution
1. **Sanear Front-end**: Reparar de inmediato el Navbar incrustando la directiva `dropdown` en el `nav-item` para recuperar la estructura grid. Reemplazar los eventos `CustomEvent` de `document` a `window` y usar los nombres correctos (`open-category-manager`, `open-beneficiary-manager`) que `beneficiary-manager.js` y `category-manager.js` esperan.
2. **Purgar "Fantasma" Gemini**: Eliminar definitivamente `backend/core/ia_engine.py` (el cual conservaba credenciales y dependencias de Google Generative AI).
3. **Restaurar Endpoints Bloqueantes**: Modificar `backend/api/v1/ia.py` (que enrutaba los llamados a `/forecast` e `/insights`) para remover el `IAEngine` muerto. Estas rutas ahora devolverán mensajes fijos (mock data) indicando que las funciones de predicción están bajo mantención hasta que un nuevo *Plugin IA* se instale. Esto detendrá la ola de Errores 500 en la app.

## Impact
- **Frontend (`base.html`)**: Correcto comportamiento visual de dropdowns y modales rehabilitadas en 100%. Reducción de carga cognitiva por interfaz limpia.
- **Backend (`ia_engine.py` eliminado y `v1/ia.py` resuelto)**: Finalización genuina del hito de eliminar IA incrustada y habilitación para el esquema de Plugins, previniendo reinicios incontrolados o bloqueos.
