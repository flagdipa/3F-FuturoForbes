# Spec: Pruebas Exhaustivas de Worker 1 (Fase 1)

## Etapas del Automailer Playwright
### Pruebas de Pantalla (Auth)
- El test en `worker_1_auth` debe navegar directamente a `http://localhost:8000/login`.
- Simularemos un flujo "Fallo de Autorización": enviar usuario aleatorio y password, interceptando el 401 sin que la interfaz se crashee en blanco y reportando si aparece efectivamente el aviso Toast/Alert.
- Simularemos una redirección a URL de registro `/register` (chequeando status 200).

### Pruebas de la Vista de Cuentas (Accounts CRUD)
- El test de `worker_1_accounts` arrancará superando el Login (`qa_test@example.com` | `Password123!`).
- Muta su navegación a `/accounts`, a la espera completa de estado de Alpine (`window.Alpine`).
- Inspecciona interacciones con Botón "Nueva Cuenta" / Modales.
- Evalúa el Dashboard de Sidebar con el selector `nav-link` correspondiente detectando si ocurre el `(reading 'sidebar')` error u otro derivado de la carga jerárquica del store "cuentas".

### Metodologías de Aserción
- El sistema almacenará TODOS los arrays de errores locales arrojados en consola de JS antes del `afterAll()`.
- Emitirá el documento `worker_1_report.md` sin fallar el proceso general del host (`openspec status`).
