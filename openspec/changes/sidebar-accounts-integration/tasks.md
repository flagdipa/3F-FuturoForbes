# Tasks: Integración de Cuentas en Sidebar y Navegación Bimonetaria

## 1. Modificaciones en el Layout (Sidebar)

- [ ] 1.1 Eliminar el ítem de navegación de "Transacciones" único en `base.html`.

### ✅ Navegación y Sidebar
- [x] Crear estado de moneda global en Alpine Store (`activeCurrency`).
- [x] Refactorizar navegación principal: "Transacciones en Pesos" y "Transacciones en Dólares".
- [x] Implementar listado dinámico de cuentas en el sidebar.
- [x] Aplicar filtros automáticos por moneda en el listado del sidebar.
- [x] Corregir estructura HTML del sidebar (eliminación de divs en uls).
- [x] Implementar filtrado suave (sin recarga) al hacer clic en cuentas desde la vista de transacciones.
- [x] Extender API Backend para soportar `/transactions/?currency=...`.
Currency`.
- [ ] 1.4 Estilizar las cuentas en el sidebar con sus saldos y colores por tipo (Asset/Liability).

## 2. Lógica del Store (Alpine.js)

- [ ] 2.1 Actualizar el store global (probablemente en un archivo base o `accounts.js`) para manejar el estado de `activeCurrency`.
- [ ] 2.2 Agregar el método `selectAccountForFiltering(id)` para emitir el evento global de cambio de filtro.
- [ ] 2.3 Sincronizar el estado del sidebar con el store de cuentas para asegurar refrescos automáticos tras transacciones.

## 3. Filtrado de Transacciones

- [ ] 3.1 Actualizar `transactions.js` para que el método de inicialización lea el parámetro `currency` de la URL o del store.
- [ ] 3.2 Escuchar el evento de selección de cuenta desde el sidebar para actualizar el filtro local `this.filters.account_id`.
- [ ] 3.3 Asegurar que al cambiar entre "Pesos" y "Dólares" en el sidebar, los filtros de la tabla se reseteen o ajusten correctamente.

## 4. Validación

- [ ] 4.1 Verificar que al seleccionar ARS, solo aparezcan cuentas de moneda ARS en el sidebar.
- [ ] 4.2 Probar que un solo clic en una cuenta del sidebar filtre la tabla de la derecha instantáneamente.
- [ ] 4.3 Comprobar la responsividad del sidebar con la nueva lista de cuentas (scroll).
