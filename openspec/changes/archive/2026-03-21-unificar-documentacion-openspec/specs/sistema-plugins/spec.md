## ADDED Requirements

### Requirement: Arquitectura de plugins con sistema de hooks
El sistema SHALL implementar una arquitectura de plugins modular inspirada en PrestaShop, permitiendo extender funcionalidades sin modificar el código core mediante un sistema de hooks.

#### Scenario: Cargar plugins activos al inicio
- **WHEN** el sistema inicia
- **THEN** el PluginManager SHALL cargar todos los plugins marcados como activos en la base de datos
- **AND** SHALL inicializar cada plugin llamando a su método initialize()
- **AND** SHALL registrar los hooks suscritos por cada plugin

#### Scenario: Registrar callback para hook
- **WHEN** un plugin llama a register_hook(hook_name, callback)
- **THEN** el PluginManager SHALL almacenar el callback asociado al hook
- **AND** SHALL permitir múltiples plugins suscritos al mismo hook
- **AND** SHALL mantener el registro en memoria durante la ejecución

#### Scenario: Disparar hook con múltiples callbacks
- **WHEN** el sistema dispara un hook (ej: transaction_created)
- **THEN** el PluginManager SHALL ejecutar todos los callbacks suscritos a ese hook
- **AND** SHALL ejecutarlos de forma asíncrona concurrente
- **AND** SHALL manejar errores individualmente (un plugin que falla no afecta a otros)
- **AND** SHALL establecer timeout de 30 segundos por callback

#### Scenario: Activar plugin dinámicamente
- **WHEN** un administrador activa un plugin desde la interfaz
- **THEN** el sistema SHALL cargar el plugin en memoria
- **AND** SHALL llamar a su método initialize()
- **AND** SHALL registrar sus hooks
- **AND** SHALL marcar el plugin como activo en la base de datos

#### Scenario: Desactivar plugin
- **WHEN** un administrador desactiva un plugin
- **THEN** el sistema SHALL llamar al método shutdown() del plugin
- **AND** SHALL remover sus callbacks de los hooks
- **AND** SHALL liberar recursos asociados
- **AND** SHALL marcar el plugin como inactivo en la base de datos

### Requirement: Clase base abstracta para plugins
El sistema SHALL proporcionar una clase BasePlugin abstracta que todos los plugins deben heredar, definiendo el contrato estándar.

#### Scenario: Implementar plugin heredando de BasePlugin
- **WHEN** un desarrollador crea un plugin que hereda de BasePlugin
- **THEN** el plugin SHALL definir nombre_tecnico, nombre_display, version, autor
- **AND** SHALL implementar los métodos abstractos initialize() y shutdown()
- **AND** SHALL definir la lista de hooks que utiliza

#### Scenario: Plugin recibe configuración al inicializar
- **WHEN** un plugin se inicializa
- **THEN** el sistema SHALL pasar la configuración almacenada (JSON) al constructor
- **AND** el plugin SHALL poder acceder a su configuración vía self.config
- **AND** el plugin SHALL validar su configuración requerida

#### Scenario: Plugin maneja hooks mediante métodos on_
- **WHEN** un plugin define métodos con prefijo on_ (ej: on_transaction_created)
- **THEN** el sistema SHALL llamar automáticamente esos métodos cuando se dispare el hook correspondiente
- **AND** SHALL pasar los parámetros definidos para ese hook

### Requirement: Gestión de configuración de plugins
El sistema SHALL permitir almacenar y modificar configuración JSON para cada plugin.

#### Scenario: Almacenar configuración de plugin
- **WHEN** un usuario guarda la configuración de un plugin
- **THEN** el sistema SHALL validar el JSON contra el schema del plugin
- **AND** SHALL almacenar la configuración en el campo configuracion del modelo Plugin
- **AND** SHALL recargar el plugin con la nueva configuración si está activo

#### Scenario: Obtener configuración actual
- **WHEN** un usuario solicita la configuración de un plugin
- **THEN** el sistema SHALL retornar el JSON almacenado
- **AND** SHALL mostrar valores por defecto para campos no configurados

#### Scenario: Validar configuración de plugin
- **WHEN** se actualiza la configuración de un plugin
- **THEN** el sistema SHALL validar contra el schema definido por el plugin
- **AND** SHALL rechazar configuración inválida con mensaje de error descriptivo

### Requirement: Hooks disponibles del sistema
El sistema SHALL proporcionar los siguientes hooks que los plugins pueden suscribir:
- transaction_created, transaction_updated, budget_alert, goal_reached
- account_sync, vault_file_upload, report_generate
- data_export, data_import, login_attempt, daily_summary, audit_event

#### Scenario: Disparar hook transaction_created
- **WHEN** se crea una nueva transacción
- **THEN** el sistema SHALL disparar el hook transaction_created
- **AND** SHALL pasar como parámetros: transaction (objeto) y user (usuario)

#### Scenario: Disparar hook budget_alert
- **WHEN** se detecta que un presupuesto ha sido excedido
- **THEN** el sistema SHALL disparar el hook budget_alert
- **AND** SHALL pasar como parámetros: budget (presupuesto) y percentage (porcentaje usado)

#### Scenario: Disparar hook login_attempt
- **WHEN** un usuario intenta iniciar sesión
- **THEN** el sistema SHALL disparar el hook login_attempt
- **AND** SHALL pasar como parámetros: user (usuario), ip (dirección IP), success (booleano)

### Requirement: Plugins de ejemplo funcionales
El sistema SHALL incluir al menos 3 plugins de ejemplo funcionales: Telegram Bot, Email SMTP, y Dolar Hoy Argentina.

#### Scenario: Plugin Telegram Bot envía notificaciones
- **WHEN** se dispara un hook suscrito (transaction_created, budget_alert, goal_reached)
- **THEN** el plugin TelegramBotPlugin SHALL enviar mensaje al chat configurado
- **AND** SHALL usar el bot_token y chat_id de su configuración
- **AND** SHALL formatear el mensaje según el tipo de evento

#### Scenario: Plugin Email SMTP envía alertas
- **WHEN** se dispara el hook budget_alert
- **THEN** el plugin EmailSMTPPlugin SHALL enviar email de alerta
- **AND** SHALL usar la configuración SMTP (host, port, username, password)
- **AND** SHALL permitir configurar qué eventos generan emails

#### Scenario: Plugin Dolar Hoy actualiza tasas
- **WHEN** se ejecuta el hook daily_summary
- **THEN** el plugin DolarHoyPlugin SHALL obtener tasas actuales de dolarapi.com
- **AND** SHALL actualizar las divisas Blue, MEP, CCL, Cripto
- **AND** SHALL guardar el historial de tasas

### Requirement: API REST para gestión de plugins
El sistema SHALL exponer endpoints REST para instalar, activar, desactivar y configurar plugins.

#### Scenario: Listar plugins instalados
- **WHEN** un usuario autenticado solicita GET /api/v1/plugins
- **THEN** el sistema SHALL retornar lista de plugins con estado (instalado/activo)
- **AND** SHALL incluir nombre, versión, autor y descripción

#### Scenario: Instalar nuevo plugin
- **WHEN** un administrador envía POST /api/v1/plugins/install con datos del plugin
- **THEN** el sistema SHALL validar el plugin
- **AND** SHALL crear registro en base de datos con estado instalado=false
- **AND** SHALL retornar el ID del plugin creado

#### Scenario: Activar plugin vía API
- **WHEN** un administrador envía POST /api/v1/plugins/{id}/activar
- **THEN** el sistema SHALL cargar el plugin en memoria
- **AND** SHALL inicializarlo y registrar sus hooks
- **AND** SHALL actualizar estado a activo=true

#### Scenario: Obtener configuración de plugin
- **WHEN** un usuario solicita GET /api/v1/plugins/{id}/config
- **THEN** el sistema SHALL retornar la configuración JSON almacenada
- **AND** SHALL incluir schema de configuración para validación frontend

#### Scenario: Actualizar configuración de plugin
- **WHEN** un administrador envía PUT /api/v1/plugins/{id}/config con JSON válido
- **THEN** el sistema SHALL validar contra schema
- **AND** SHALL actualizar la configuración en base de datos
- **AND** SHALL recargar el plugin si está activo

#### Scenario: Obtener logs de plugin
- **WHEN** un usuario solicita GET /api/v1/plugins/{id}/logs
- **THEN** el sistema SHALL retornar los últimos logs del plugin
- **AND** SHALL permitir paginación y filtrado por nivel (INFO, WARNING, ERROR)

### Requirement: Interfaz web para gestión de plugins
El sistema SHALL proporcionar una interfaz web en /plugins para gestionar plugins.

#### Scenario: Ver lista de plugins en UI
- **WHEN** un usuario navega a /plugins
- **THEN** el sistema SHALL mostrar tabla con todos los plugins
- **AND** SHALL mostrar toggle switch para activar/desactivar cada uno
- **AND** SHALL mostrar indicador visual del estado (activo/inactivo)

#### Scenario: Configurar plugin desde UI
- **WHEN** un usuario hace clic en "Configurar" de un plugin
- **THEN** el sistema SHALL abrir modal con formulario dinámico
- **AND** SHALL generar campos basados en el schema JSON de configuración
- **AND** SHALL validar antes de guardar

#### Scenario: Ver logs de plugin en UI
- **WHEN** un usuario hace clic en "Ver logs" de un plugin
- **THEN** el sistema SHALL mostrar ventana con logs del plugin
- **AND** SHALL permitir filtrar por nivel y fecha
- **AND** SHALL auto-refrescar cada 30 segundos

### Requirement: Registro de auditoría de plugins
El sistema SHALL registrar todas las operaciones de activación/desactivación de plugins para auditoría.

#### Scenario: Registrar activación de plugin
- **WHEN** un plugin es activado
- **THEN** el sistema SHALL crear registro de auditoría
- **AND** SHALL incluir: usuario, fecha/hora, plugin_id, acción (ACTIVATE)

#### Scenario: Registrar desactivación de plugin
- **WHEN** un plugin es desactivado
- **THEN** el sistema SHALL crear registro de auditoría
- **AND** SHALL incluir: usuario, fecha/hora, plugin_id, acción (DEACTIVATE)

#### Scenario: Registrar cambio de configuración
- **WHEN** se actualiza la configuración de un plugin
- **THEN** el sistema SHALL crear registro de auditoría
- **AND** SHALL registrar usuario, cambios realizados (old_values, new_values)

### Requirement: Aislamiento de errores de plugins
El sistema SHALL aislar errores de plugins para que un plugin que falla no afecte el funcionamiento del sistema ni de otros plugins.

#### Scenario: Manejar error en callback de hook
- **WHEN** un plugin lanza excepción durante ejecución de hook
- **THEN** el sistema SHALL capturar el error
- **AND** SHALL registrar el error en logs del plugin
- **AND** SHALL continuar ejecutando otros callbacks del mismo hook
- **AND** SHALL NOT afectar la operación principal del sistema

#### Scenario: Timeout en ejecución de plugin
- **WHEN** un callback de plugin excede el timeout (30 segundos)
- **THEN** el sistema SHALL cancelar la ejecución
- **AND** SHALL registrar timeout en logs
- **AND** SHALL continuar con otros callbacks
- **AND** SHALL NOT bloquear la ejecución del sistema

#### Scenario: Recuperación de plugin fallido
- **WHEN** un plugin falla al inicializar
- **THEN** el sistema SHALL marcar el plugin como inactivo
- **AND** SHALL registrar el error
- **AND** SHALL permitir reintentar activación después de corregir el problema
