# Spec: E2E Verification Plan

## Pruebas de Autenticación
- Validar redirección sin sesión activa.
- Validar login exitoso y retención de token.
- Validar "Log Out" limpio.

## Pruebas de Entidades y Catálogos (CRUD)
- **Cuentas**: Acceder a `/accounts`, añadir una cuenta de banco ficticia, validar que aparezca en el listado y que los balances carguen en el dashboard lateral.
- **Categorías**: Acceder a `/categories`, verificar carga del árbol/lista, crear nodo.
- **Beneficiarios**: Acceder a `/payees`, crear beneficiario, verificar persistencia.

## Pruebas de Transacciones y Flujos Complejos
- Interactuar con la pantalla `/transactions`.
- Generar un **Ingreso** simple.
- Generar un **Gasto** recurriendo a Split (validar coherencia entre los montos de frontend y la respuesta de API).
- Prueba del subidor **OCR**: Enviar archivo de imagen de prueba, manejar la respuesta (esperar éxito o un error controlado, pero NUNCA un fallo de frontend silencioso/crítico).

## Pruebas de Presupuestos y Metas (V2 Models)
- Acceder a `/budgets` y crear una línea de presupuesto.
- Acceder a `/goals` y establecer una meta de ahorro base.

## Criterios de Éxito de la Ejecución E2E
- El script de Playwright debe atrapar y reportar fallos de red (Status Code 4xx/5xx).
- El navegador capturará los `console.error` de JavaScript para reportar problemas de AlpineJS (e.g. `$store.sidebar` es nulo, x-data errores).
- Al finalizar, el script entregará un reporte de consistencia o directamente una lista de **incidencias encontradas**.
