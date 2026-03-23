# Design: System Critical Hotfixes V1

## Context
La arquitectura frontend y backend quedó expuesta a efectos colaterales. Frontend fue sobrecargado y al arreglar el Sidebar se omitieron clases requeridas por AdminLTE y Bootstrap (Dropdowns rotos). El backend sufre interrupciones porque rutinas como Insights y Forecast continúan requiriendo una instancia global de la librería `google.generativeai` que ya fue descalificada durante la limpieza de deuda técnica anterior.

## Goals
- Reparar la navegación en el menú alto de la aplicación devolviéndole su correcta estructura e interacciones CSS/JS.
- Consolidar la erradicación del componente Gemini, resolviendo permanentemente dependencias perdidas y mejorando robustez del back-end.

## Technical Approach

### 1. Limpieza HTML / UI
Modificar `frontend/templates/base.html`:
- Buscar `<li class="nav-item">` que aloja a `<a data-bs-toggle="dropdown">`. Convertirla a `<li class="nav-item dropdown">` para devolver el diseño en caja original a todo el menú de herramientas.
- Reprogramar la acción de los botones de herramientas para que el DOM global logre llamar los Listeners exactos que usa Alpine.js:
  - De: `document.dispatchEvent(new CustomEvent('open-beneficiaries'))`
  - A: `window.dispatchEvent(new CustomEvent('open-beneficiary-manager'))`
  - De: `document.dispatchEvent(new CustomEvent('open-categories'))`
  - A: `window.dispatchEvent(new CustomEvent('open-category-manager'))`

### 2. Saneamiento Backend
- **Eliminación Absoluta:** Borrar `backend/core/ia_engine.py`. Esta reliquia usa recursos sin justificación luego del paso al motor modular de Plugins.
- **Mock Seguro Endpoints V1:** Editemos `backend/api/v1/ia.py`. Retirar los *Imports* a `IAEngine`. Mantendremos las firmas `/forecast` y `/insights` devolviendo arreglos JSON estáticos simulados. Cuando se habilite el módulo formal de predicción, en el futuro, estos apuntarán a ese nuevo plugin. Por ahora, regresarán un `dict` inocuo garantizando que la UI web o móvil no colapse con falsos 500 Server Error en el Dashboard.

## Risks
- Modificar el router de `ia.py` asegura que cualquier intento futuro en Dashboard de consumir esas APIs mostrarán datos genéricos. El usuario es consciente ya que él mismo prohibió explícitamente el uso de Gemini Inline y sugirió convertirlo en un Plugin a voluntad más adelante.
