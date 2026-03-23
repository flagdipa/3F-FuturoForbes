# Design: Emergency UI Layout Fix & Relocate Tools

## Context
El Sidebar de 3F está visualmente sobrecargado y presenta inconsistencias reportadas de deformación en el CSS o estructura HTML de AdminLTE, en gran medida debido a la redundancia de los botones para abrir Modales (Categorías y Beneficiarios). Por pedido urgente, estos deben alojarse **solamente** en el menú superior.

## Goals
- Reparar y estabilizar la UI.
- Mover los componentes de "Beneficiarios" y "Categorías" al dropdown "Herramientas" (`<i class="fa-solid fa-screwdriver-wrench"></i>`) en el navbar superior (`<nav class="app-header">`).
- Remover el código duplicado y sobrante del Sidebar para aliviar la altura y evitar glitches (overlapping, overflow problems) y simplificar el uso.

## Technical Approach

### 1. Limpieza de `base.html` (Top Menu Navbar)
Actualmente el bloque "Herramientas" en el top menu tiene enlaces rotos o a URLs muertas (`/beneficiarios`).
Será modificado de la siguiente forma:

```html
<ul class="dropdown-menu dropdown-menu-dark border-secondary">
    <li>
        <a class="dropdown-item" href="#" onclick="document.dispatchEvent(new CustomEvent('open-beneficiaries')); event.preventDefault();">
            <i class="fa-solid fa-users small me-2 text-primary"></i> 
            <span x-text="$store.lang.t('nav.beneficiaries')">Gestión Beneficiarios</span>
        </a>
    </li>
    <li>
        <a class="dropdown-item" href="#" onclick="document.dispatchEvent(new CustomEvent('open-categories')); event.preventDefault();">
            <i class="fa-solid fa-tags small me-2 text-warning"></i> 
            <span x-text="$store.lang.t('nav.categories')">Gestión Categorías</span>
        </a>
    </li>
</ul>
```
*(Se usarán iconos y traducciones estándar de la app, eliminando el `/entidades` descontinuado o enlaces rotos).*

### 2. Limpieza de `base.html` (Sidebar)
Se **eliminará enteramente** el bloque de código que introdujo el error anterior:
```html
<li class="nav-header" x-text="$store.lang.t('common.tools')">HERRAMIENTAS</li>
<li class="nav-item">
    <a href="#" @click.prevent="document.dispatchEvent(new CustomEvent('open-beneficiaries'))" ...>
        ...
    </a>
</li>
<li class="nav-item">
    <a href="#" @click.prevent="document.dispatchEvent(new CustomEvent('open-categories'))" ...>
        ...
    </a>
</li>
```
Al quitar estos items excesivos (`nav-header` inclusive), el UI recupera normalidad en resolución desktop y tablet sin tener tanto peso visual, solucionando el desorden percibido.

## Risks
- **Modal Event Handling:** Las modales se cargan al final de `base.html` y escuchan `window.addEventListener('open-categories', ...)`. Disparar `document.dispatchEvent()` desde un `<a onclick="">` de top navbar puede reaccionar de forma sutilmente diferente a un evento de alpine, pero usando sintaxis Javascript Vanilla garantizará la ejecución. `window.dispatchEvent` será preferido si la modal de categorías está atada ahí.
