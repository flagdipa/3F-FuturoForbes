# Spec: Seguridad y Auditoría

## Goal
Centralizar y consolidar la documentación del módulo de seguridad y registros inmutables del sistema 3F (Futuro Forbes). Garantizar un entendimiento profundo sobre cómo se manejan la autenticación (JWT), la prevención de abusos (Rate Limiting) y el registro estricto e inmutable de operaciones (Auditoría).

## Capabilities

Esta especificación cubre la capa de protección y trazabilidad del backend:

1. **Autenticación y Sesión:**
   - Emisión y validación de JSON Web Tokens (JWT) mediante `PyJWT`.
   - Hash seguro de contraseñas empleando `Passlib` (bcrypt).
   - Renovación de sesiones (Refresh tokens) y manejo seguro del ciclo de vida de la cuenta (flujos de recuperación y reseteo).

2. **Auditoría Integral (AuditTrail):**
   - Registro inmutable de absolutamente todas las operaciones sensibles (CRUD) mediante inyección en la capa de servicios o middleware.
   - Generación de trazas detalladas conteniendo metadatos como dirección IP, User-Agent, qué entidad se tocó, los valores antiguos completos (snapshot) y los nuevos valores ingresados en JSON.
   - Cumplimiento de estándares mínimos de trazabilidad (similares a normativas GDPR para logs de transacciones financieras).

3. **Prevención y Sanitización:**
   - Control de cadencia y volumen HTTP (Rate limiting) proveído transversalmente por `SlowAPI`.
   - Limpieza y sanitización de payloads y campos HTML insertados pos los usuarios (principalmente para descripciones o notas) mediante `Bleach`.

## Data Models

Toda la persistencia relativa a la identidad y a sus pasos dentro de la app radica en `User` y `AuditLog`:

### User
```python
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    created_at: datetime
    ...
```

### AuditLog
```python
class AuditLog(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    action: str # ENUM(CREATE, UPDATE, DELETE, LOGIN, LOGOUT, EXPORT)
    entity_type: str # Ej: 'transaction', 'account', 'budget'
    entity_id: Optional[int] = None
    old_values: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    new_values: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    ip_address: str
    user_agent: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

## API Endpoints

Las operaciones están mayormente localizadas bajo el paraguas de `/auth` y `/audit` (`/api/v1`):

- **`/auth`**
  - `POST /register` - Crear nueva cuenta.
  - `POST /login` - Login obteniendo JWT / Session.
  - `POST /logout` - Invalidar sesión activa.
  - `POST /refresh` - Emitir JWT fresco.
  - `POST /forgot-password` - Solicitar token de recuperación.
  - `POST /reset-password` - Efectuar cambio de password vía token.
  - `GET /me` - Obtener claims de identidad propios.
  - `PUT /me` - Actualizar biografía o perfil base propiamente logueado.

- **`/audit`**
  - `GET /logs` - Listar entradas granulares paginadas del sistema.
  - `GET /logs/{id}` - Detalles de cambios JSON (Before and After).
  - `GET /export` - Dump masivo csv/pdf del histórico.

## Scenarios

- **Scenario: Generación Implícita de Auditoría por Modificación de Transacción**
  - *Given* un `User` que está logueado y altera el total de un ticket registrado ayer. El router valida el JWT.
  - *When* el método `update_transaction` de la API recibe un `PUT /transactions/42`.
  - *Then* el servicio de auditoría inyecta una nueva fila en `AuditLog` guardando automáticamente en el chunk JSON (`old_values`) el objeto completo de la transacción anterior, y en `new_values` el nuevo. Registra la IP de quien despachó el PUT (ej. "192.168.1.13") y el agente de Playwright o el Browser empleado.

- **Scenario: Frenado por SlowAPI (DDoS u Overload)**
  - *Given* un endpoint fuertemente vigilado como `POST /auth/login`.
  - *When* se mandan más de 5 peticiones erróneas en 1 minuto desde el mismo IP.
  - *Then* la respuesta de la capa del framework lanza un TypeError de FastAPI y el middleware intercepta, devolviendo un HTTP `429 Too Many Requests` (SlowAPI). El ataque jamás toca la base de datos de usuarios.
