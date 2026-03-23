# Tasks: System Critical Hotfixes V1

## 1. UI & Layout (Navbar)
- [x] 1.1 En `frontend/templates/base.html` buscar `<li class="nav-item">` que aloja el dropdown de herramientas y cambiar la clase a `nav-item dropdown`.
- [x] 1.2 En el mismo código `.dropdown-menu` restaurar los eventos de las filas `Gestión de Beneficiarios` y `Gestión de Categorías` desde `document.dispatchEvent('open-X')` hacia el comando literal `window.dispatchEvent(new CustomEvent('open-beneficiary-manager'))` y `window.dispatchEvent(new CustomEvent('open-category-manager'))`.

## 2. Purgar Gemini Fantasma (Backend)
- [x] 2.1 Eliminar (borrar fisicamente del disco) el archivo obsoleto `backend/core/ia_engine.py`. Dicha funcionalidad fue erradicada parcialmente antes y dejaba un *crash*.
- [x] 2.2 Modificar `backend/api/v1/ia.py`. Eliminar el import a `IAEngine`. Modificar la función `/forecast` suprimiendo llamadas a `ia_service` y haciendo que simplemente devuelva el mock de diccionarios hardcodeado en la misma clase o devuelva `{ "predicted_income": [0,0,0], "predicted_expenses": [0,0,0], "status": "offline" }`. Modificar la función `/insights` para que devuelva un Array falso de sugerencias tipo `[{"type": "info", "title": "Dashboard IA Offline", "desc": "Instala un Plugin para retomar"}]`. Eliminar o reestructurar todo uso de `ia_service.X()`.

## 3. Verificación
- [x] 3.1 Probar mediante `pytest backend/tests/` o arrancar en modo prueba para asegurar que las dependencias muertas no impidan al servidor correr.
