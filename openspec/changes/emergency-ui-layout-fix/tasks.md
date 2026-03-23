# Tasks: Emergency UI Layout Fix & Relocate Tools

## 1. Top Navbar Optimization
- [x] 1.1 En `frontend/templates/base.html` buscar la clase `.app-header` y su menú desplegable de "Herramientas" (el ícono `fa-screwdriver-wrench`). Eliminar los ítems obsoletos ("Gestión de Entidades" `/entidades` y "Gestión de Cuentas" `/accounts`).
- [x] 1.2 Reemplazar los ítems restantes para mantener solo: "Gestión Beneficiarios" (gatillando `onclick="document.dispatchEvent(new CustomEvent('open-beneficiaries')); event.preventDefault();"`) y "Gestión Categorías" (gatillando `onclick="document.dispatchEvent(new CustomEvent('open-categories')); event.preventDefault();"`).

## 2. Sidebar Layout Fix
- [x] 2.1 En `frontend/templates/base.html` buscar la clase `.sidebar-menu`. Eliminar las etiquetas `<li class="nav-header">HERRAMIENTAS</li>` y los `<li class="nav-item">` asociados a **Beneficiarios** y **Categorías** que fueron agregados por error en despliegues recientes para aliviar la sobrecarga visual de la pantalla.
