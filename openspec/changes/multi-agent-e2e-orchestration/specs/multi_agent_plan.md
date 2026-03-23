# Spec: Plan de Pruebas Distribuidas (Multi-Agente)

## Roles y Separación Funcional (Criterio de Ejecución en Paralelo)
### 1. Agente Orquestador (Master)
- **Responsabilidad principal**: Setup del Servidor (Uvicorn test env), creación inicial de artefactos MD vacíos para los Workers y compilación final.
- **Flujo de salida**: Lee todos los `worker_*_report.md` del sistema y formula el sumario final indexando los bugs de UI, Red y Backend.

### 2. Agente 1 (Worker Auth & Cuentas)
- Pruebas E2E de inicio de sesión (`/login`, `/register`).
- Creación, listado y borrado de `Accounts` (Banco imaginario).
- **Artefacto de Respuesta**: `worker_1_report.md` con listado de crashes o éxitos.

### 3. Agente 2 (Worker Entidades & Categorías)
- Pruebas E2E en menús `/categories` (Interacción del DOM en árbol anidado, creación).
- Pruebas E2E en menú `/payees` (Crear Beneficiario, listar y asociar).
- **Artefacto de Respuesta**: `worker_2_report.md`.

### 4. Agente 3 (Worker Transacciones E2E)
- Formulario de alta de **Ingreso/Gasto**, manipulación de Fechas, validación de splits numéricos para que Frontend cuadre con Backend.
- Verificación del popup / vista OCR.
- Validación en Presupuestos `/budgets`.
- **Artefacto de Respuesta**: `worker_3_report.md`.

## Mecanismos de Fallo y Aserción
Ninguno de los agentes intentará corregir el código **inmediatamente** si encuentra un fallo durante su test (ya sea un bug visual o error 500 del servidor). La misión es recolectar a través del log y solo reparar posteriormente si se invoca `/opsx-apply` específicamente para "hotfixing".
