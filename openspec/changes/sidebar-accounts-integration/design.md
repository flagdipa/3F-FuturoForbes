# Design: Integración de Cuentas en el Sidebar

## Context

El sistema ya cuenta con un `accounts.js` (Alpine Store) que gestiona el listado de cuentas. Actualmente, este se usa principalmente en el modal de gestión y en los dropdowns de las transacciones. El usuario desea que estas cuentas asuman un rol protagónico en el Sidebar para navegación rápida.

## Goals

*   **Navegación Bimonetaria:** Reemplazar el ítem "Transacciones" único por dos ítems permanentes: "Transacciones Pesos" y "Transacciones Dól.".
*   **Filtrado Dinámico de Cuentas:** Al seleccionar ARS o USD, las cuentas listadas en el sidebar se filtrarán automáticamente para mostrar solo las que manejan dicha moneda.

## Non-Goals

*   Crear un nuevo endpoint de backend (se usará el existente).
*   Permitir edición de saldos directamente desde el sidebar.

## Proposed Changes

### 1. Sidebar (base.html)
Implementar un selector de contexto de moneda en el sidebar:
```html
<li class="nav-item">
    <a href="/transacciones?currency=ARS" class="nav-link" :class="activeCurrency==='ARS' ? 'active' : ''" @click="activeCurrency='ARS'">
        <i class="nav-icon fa-solid fa-money-bill-wave text-success"></i>
        <p>Transacciones Pesos</p>
    </a>
</li>
<li class="nav-item">
    <a href="/transacciones?currency=USD" class="nav-link" :class="activeCurrency==='USD' ? 'active' : ''" @click="activeCurrency='USD'">
        <i class="nav-icon fa-solid fa-dollar-sign text-info"></i>
        <p>Transacciones Dólares</p>
    </a>
</li>
```
Y filtrar el listado de cuentas según `activeCurrency`:
```html
<template x-for="acc in $store.accounts.list.filter(a => a.currency === activeCurrency)">
    ...
</template>
```

### 2. Alpine Store (accounts.js)
Agregar un método helper `selectAccountForFiltering(id)` que guarde el ID seleccionado y despache un evento global al que el componente `transactions` esté escuchando.

### 3. Vista de Transacciones (transactions.js)
Escuchar el evento `account-selected` o verificar periódicamente el store para actualizar su filtro local `this.filters.account_id` y llamar a `applyFilters()`.

## Risks / Trade-offs

*   **Espacio:** Si hay muchas cuentas, el sidebar puede volverse muy largo. **Solución:** Mantenerlo dentro de un contenedor scrollable o permitir colapsar el bloque.
*   **Consistencia:** El saldo en el sidebar debe refrescarse cuando se guarda una transacción. Ya está implementado vía el evento `transactions-updated`.
