## ADDED Requirements

### Requirement: Autenticación basada en JWT
El sistema SHALL implementar autenticación mediante JSON Web Tokens (JWT) con algoritmo HS256, tokens de acceso de 60 minutos y tokens de refresco de 7 días.

#### Scenario: Login exitoso genera tokens JWT
- **WHEN** un usuario proporciona credenciales válidas (email y contraseña)
- **THEN** el sistema SHALL verificar el hash bcrypt de la contraseña
- **AND** SHALL generar access_token con expiración de 60 minutos
- **AND** SHALL generar refresh_token con expiración de 7 días
- **AND** SHALL retornar ambos tokens al cliente

#### Scenario: Acceder a endpoint protegido con token válido
- **WHEN** un cliente envía petición a endpoint protegido con header Authorization: Bearer <token>
- **THEN** el sistema SHALL validar la firma del token
- **AND** SHALL verificar que el token no haya expirado
- **AND** SHALL extraer user_id del payload del token
- **AND** SHALL permitir el acceso al endpoint

#### Scenario: Rechazar token expirado
- **WHEN** un cliente usa un access_token expirado
- **THEN** el sistema SHALL rechazar la petición con código 401
- **AND** SHALL retornar error "Token expirado"
- **AND** SHALL sugerir usar refresh_token para obtener nuevo access_token

#### Scenario: Refrescar token de acceso
- **WHEN** un cliente envía refresh_token válido a /auth/refresh
- **THEN** el sistema SHALL verificar el refresh_token
- **AND** SHALL generar nuevo access_token
- **AND** SHALL mantener el mismo refresh_token o generar uno nuevo

#### Scenario: Logout invalida tokens
- **WHEN** un usuario realiza logout
- **THEN** el sistema SHALL invalidar el access_token actual
- **AND** SHALL invalidar el refresh_token asociado
- **AND** SHALL registrar el evento de logout en auditoría

### Requirement: Hash seguro de contraseñas
El sistema SHALL utilizar bcrypt con 12 rounds para almacenar contraseñas de forma segura.

#### Scenario: Crear usuario con contraseña hasheada
- **WHEN** se registra un nuevo usuario
- **THEN** el sistema SHALL generar salt aleatorio
- **AND** SHALL aplicar bcrypt con 12 rounds a la contraseña
- **AND** SHALL almacenar solo el hash, nunca la contraseña en texto plano

#### Scenario: Verificar contraseña en login
- **WHEN** un usuario intenta iniciar sesión
- **THEN** el sistema SHALL obtener el hash almacenado
- **AND** SHALL aplicar bcrypt a la contraseña proporcionada
- **AND** SHALL comparar de forma segura contra tiempo constante
- **AND** SHALL permitir acceso solo si coinciden

#### Scenario: Cambiar contraseña
- **WHEN** un usuario actualiza su contraseña
- **THEN** el sistema SHALL requerir la contraseña actual
- **AND** SHALL validar que la nueva contraseña cumple requisitos de seguridad
- **AND** SHALL generar nuevo hash bcrypt
- **AND** SHALL invalidar sesiones existentes

### Requirement: Control de acceso basado en roles (RBAC)
El sistema SHALL implementar RBAC con roles: user, admin, superuser, permitiendo acceso granular a recursos.

#### Scenario: Usuario con rol "user" accede solo a sus datos
- **WHEN** un usuario con rol "user" solicita recursos
- **THEN** el sistema SHALL filtrar resultados para mostrar solo sus datos
- **AND** SHALL rechazar acceso a datos de otros usuarios
- **AND** SHALL retornar código 403 si intenta acceder a recursos ajenos

#### Scenario: Usuario con rol "admin" accede a funciones administrativas
- **WHEN** un usuario con rol "admin" accede a panel de administración
- **THEN** el sistema SHALL permitir gestión de usuarios y configuración
- **AND** SHALL permitir ver logs del sistema
- **AND** SHALL NOT permitir acceso a funciones de superuser

#### Scenario: Verificar permisos antes de operación
- **WHEN** se intenta realizar operación restringida
- **THEN** el sistema SHALL verificar el rol del usuario
- **AND** SHALL verificar permisos específicos para el recurso
- **AND** SHALL permitir o denegar según RBAC

### Requirement: Rate limiting para prevención de abuso
El sistema SHALL implementar rate limiting: 100 requests/minuto general, 5 requests/minuto para auth, 10 requests/minuto para IA.

#### Scenario: Limitar requests generales
- **WHEN** una IP excede 100 requests por minuto
- **THEN** el sistema SHALL retornar código 429 (Too Many Requests)
- **AND** SHALL incluir header Retry-After con tiempo de espera
- **AND** SHALL registrar el evento de rate limiting

#### Scenario: Limitar intentos de login
- **WHEN** una IP intenta más de 5 logins por minuto
- **THEN** el sistema SHALL bloquear intentos adicionales
- **AND** SHALL retornar código 429
- **AND** SHALL registrar como posible ataque de fuerza bruta

#### Scenario: Limitar requests de IA
- **WHEN** un usuario excede 10 requests por minuto a endpoints de IA
- **THEN** el sistema SHALL retornar código 429
- **AND** SHALL sugerir esperar antes de reintentar

### Requirement: Logs de auditoría inmutables
El sistema SHALL registrar todas las operaciones CRUD y eventos de seguridad en logs de auditoría que NO pueden ser editados ni eliminados por usuarios.

#### Scenario: Registrar creación de entidad
- **WHEN** se crea cualquier entidad (cuenta, transacción, categoría, etc.)
- **THEN** el sistema SHALL crear registro de auditoría con action=CREATE
- **AND** SHALL incluir: user_id, entity_type, entity_id, new_values (JSON)
- **AND** SHALL incluir timestamp, IP address, user agent

#### Scenario: Registrar actualización de entidad
- **WHEN** se actualiza cualquier entidad
- **THEN** el sistema SHALL crear registro de auditoría con action=UPDATE
- **AND** SHALL incluir old_values y new_values (diff)
- **AND** SHALL registrar qué campos cambiaron

#### Scenario: Registrar eliminación de entidad
- **WHEN** se elimina (soft delete) cualquier entidad
- **THEN** el sistema SHALL crear registro de auditoría con action=DELETE
- **AND** SHALL incluir old_values completos antes de eliminar
- **AND** SHALL registrar quién y cuándo eliminó

#### Scenario: Registrar eventos de login/logout
- **WHEN** un usuario inicia o cierra sesión
- **THEN** el sistema SHALL crear registro con action=LOGIN o LOGOUT
- **AND** SHALL incluir éxito/fracaso del intento
- **AND** SHALL registrar IP y user agent

#### Scenario: Registrar operaciones de exportación
- **WHEN** un usuario exporta datos (PDF, Excel, CSV)
- **THEN** el sistema SHALL crear registro con action=EXPORT
- **AND** SHALL incluir formato, filtros aplicados, cantidad de registros
- **AND** SHALL registrar propósito de exportación si se proporciona

#### Scenario: Impedir modificación de logs
- **WHEN** se intenta modificar o eliminar un registro de auditoría
- **THEN** el sistema SHALL rechazar la operación
- **AND** SHALL retornar código 403
- **AND** SHALL registrar intento de manipulación

### Requirement: Protección de datos sensibles
El sistema SHALL cifrar datos sensibles en tránsito (TLS 1.3) y en reposo, sanitizar inputs HTML, y validar todos los datos con Pydantic.

#### Scenario: Cifrar comunicación con TLS 1.3
- **WHEN** el sistema recibe o envía datos por red
- **THEN** SHALL usar TLS 1.3 para cifrar conexiones
- **AND** SHALL rechazar conexiones no cifradas en producción

#### Scenario: Sanitizar inputs HTML
- **WHEN** se recibe input de usuario que podría contener HTML
- **THEN** el sistema SHALL usar Bleach para sanitizar
- **AND** SHALL remover scripts y tags peligrosos
- **AND** SHALL permitir solo tags seguros (p, br, strong, em)

#### Scenario: Validar datos con Pydantic
- **WHEN** se reciben datos en API endpoints
- **THEN** el sistema SHALL validar con modelos Pydantic
- **AND** SHALL rechazar datos que no cumplan el schema
- **AND** SHALL retornar errores descriptivos de validación

### Requirement: Headers de seguridad HTTP
El sistema SHALL incluir headers de seguridad: HSTS, CSP, X-Frame-Options, X-Content-Type-Options.

#### Scenario: Incluir header HSTS
- **WHEN** el sistema responde a peticiones HTTPS
- **THEN** SHALL incluir header Strict-Transport-Security
- **AND** SHALL forzar HTTPS por mínimo 1 año

#### Scenario: Incluir Content Security Policy
- **WHEN** el sistema sirve páginas HTML
- **THEN** SHALL incluir header Content-Security-Policy
- **AND** SHALL restringir fuentes de scripts, estilos e imágenes
- **AND** SHALL prevenir ejecución de scripts inline no autorizados

#### Scenario: Proteger contra clickjacking
- **WHEN** el sistema responde peticiones
- **THEN** SHALL incluir header X-Frame-Options: DENY
- **AND** SHALL impedir que la aplicación sea embebida en iframes

#### Scenario: Prevenir MIME sniffing
- **WHEN** el sistema sirve archivos
- **THEN** SHALL incluir header X-Content-Type-Options: nosniff
- **AND** SHALL forzar navegador a respetar Content-Type declarado

### Requirement: CORS configurado
El sistema SHALL configurar CORS para permitir solo orígenes específicos según el ambiente.

#### Scenario: Permitir origen en desarrollo
- **WHEN** el sistema corre en modo desarrollo
- **THEN** SHALL permitir peticiones desde localhost
- **AND** SHALL permitir credenciales

#### Scenario: Restringir origen en producción
- **WHEN** el sistema corre en producción
- **THEN** SHALL permitir solo dominios autorizados
- **AND** SHALL rechazar orígenes no listados
- **AND** SHALL registrar intentos desde orígenes bloqueados

### Requirement: Seguimiento de IP y User Agent
El sistema SHALL registrar IP address y User Agent para todas las operaciones de auditoría.

#### Scenario: Capturar IP del cliente
- **WHEN** se registra evento de auditoría
- **THEN** el sistema SHALL capturar IP del cliente
- **AND** SHALL manejar X-Forwarded-For para proxies
- **AND** SHALL validar formato de IP

#### Scenario: Capturar User Agent
- **WHEN** se registra evento de auditoría
- **THEN** el sistema SHALL capturar User-Agent header
- **AND** SHALL almacenar como texto
- **AND** SHALL usar para análisis de dispositivos/usuarios

### Requirement: Retención de logs
El sistema SHALL retener logs de auditoría por configuración (default: 2 años) y permitir exportación.

#### Scenario: Configurar período de retención
- **WHEN** un administrador configura retención de logs
- **THEN** el sistema SHALL aplicar el período configurado
- **AND** SHALL eliminar logs más antiguos que el período (solo si es seguro legalmente)

#### Scenario: Exportar logs de auditoría
- **WHEN** un administrador solicita exportación de logs
- **THEN** el sistema SHALL generar archivo con logs en rango de fechas
- **AND** SHALL soportar formatos CSV y JSON
- **AND** SHALL registrar quién exportó los logs
