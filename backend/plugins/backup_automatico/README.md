# Plugin Backup Automático

Plugin para 3F (Futuro Forbes) que crea copias de seguridad automáticas de la base de datos MySQL.

## 📋 Características

- ✅ **Backup automático** de base de datos MySQL usando `mysqldump`
- ✅ **Compresión gzip** opcional para ahorrar espacio
- ✅ **Almacenamiento dual**: Local y/o AWS S3
- ✅ **Retención configur**: Elimina backups antiguos automáticamente
- ✅ **Programación flexible**: Diario, semanal o mensual
- ✅ **Notificaciones**: Integración con plugin email_smtp
- ✅ **Estadísticas**: Monitoreo de backups realizados

## 🚀 Instalación

### 1. Instalar Dependencias

```bash
cd backend/plugins/backup_automatico
pip install -r requirements.txt
```

### 2. Registrar el Plugin

```bash
cd ../../../
python scripts/register_backup_plugin.py
```

### 3. Configurar el Plugin

Vía API:
```bash
# Obtener ID del plugin
GET /api/plugins/

# Actualizar configuración
PUT /api/plugins/{id}/config
{
  "enabled": true,
  "frequency": "daily",
  "backup_time": "02:00",
  "retention_days": 30,
  "compression": true,
  "local_path": "backups/",
  "s3": {
    "enabled": true,
    "bucket": "mi-bucket-s3",
    "access_key": "AKIA...",
    "secret_key": "...",
    "region": "us-east-1",
    "prefix": "3f-backups/"
  },
  "notifications": {
    "on_success": false,
    "on_failure": true
  }
}
```

### 4. Activar el Plugin

```bash
POST /api/plugins/{id}/activar
```

## ⚙️ Configuración

### Opciones de Configuración

| Opción | Tipo | Default | Descripción |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Habilitar/deshabilitar el plugin |
| `frequency` | string | `"daily"` | Frecuencia: `daily`, `weekly`, `monthly` |
| `backup_time` | string | `"02:00"` | Hora del backup (formato 24h) |
| `retention_days` | integer | `30` | Días de retención de backups |
| `compression` | boolean | `true` | Comprimir backups con gzip |
| `local_path` | string | `"backups/"` | Directorio local para backups |

### Configuración AWS S3

| Opción | Tipo | Descripción |
|--------|------|-------------|
| `s3.enabled` | boolean | Habilitar subida a S3 |
| `s3.bucket` | string | Nombre del bucket S3 |
| `s3.access_key` | string | AWS Access Key ID |
| `s3.secret_key` | string | AWS Secret Access Key |
| `s3.region` | string | Región AWS (ej: `us-east-1`) |
| `s3.prefix` | string | Prefijo para objetos en S3 |

### Notificaciones

| Opción | Tipo | Default | Descripción |
|--------|------|---------|-------------|
| `notifications.on_success` | boolean | `false` | Notificar cuando el backup es exitoso |
| `notifications.on_failure` | boolean | `true` | Notificar cuando el backup falla |

## 🔌 Hooks

El plugin se suscribe a los siguientes hooks:

### `daily_summary`
Verifica si debe ejecutar un backup según la frecuencia y hora configuradas.

### `audit_event`
Loguea operaciones de backup para auditoría.

## 📊 API Endpoints

### Probar Plugin
```bash
POST /api/plugins/{id}/test
```

### Obtener Estadísticas
El plugin expone el método `get_backup_stats()` que retorna:
```json
{
  "local_backups": 10,
  "local_size_total": 52428800,
  "local_size_formatted": "50.0 MB",
  "oldest_backup": "2026-01-01T02:00:00",
  "newest_backup": "2026-01-10T02:00:00",
  "s3_backups": 10
}
```

## 🗂️ Estructura de Backups

### Nomenclatura de Archivos
```
3f_backup_YYYYMMDD_HHMMSS.sql.gz
```

Ejemplo: `3f_backup_20260216_143052.sql.gz`

### Estructura en S3
```
3f-backups/
├── 2026/
│   ├── 01/
│   │   ├── 3f_backup_20260101_020000.sql.gz
│   │   └── 3f_backup_20260102_020000.sql.gz
│   └── 02/
│       └── 3f_backup_20260216_143052.sql.gz
```

## 🔧 Variables de Entorno

El plugin detecta automáticamente la configuración de la base de datos desde:

1. **DATABASE_URL**: URL de conexión (ej: `mysql+pymysql://user:pass@localhost:3306/3f_db`)
2. **Variables individuales**:
   - `DB_HOST` (default: localhost)
   - `DB_PORT` (default: 3306)
   - `DB_USER` (default: root)
   - `DB_PASSWORD` (default: vacío)
   - `DB_NAME` (default: 3f_db)

## 🧪 Testing

### Probar Backup Manual
```python
from backend.core.plugin_manager import plugin_manager

plugin = plugin_manager.get_plugin_instance("backup_automatico")
await plugin.create_backup()
```

### Verificar Configuración
```python
stats = await plugin.get_backup_stats()
print(stats)
```

## 📝 Logs

El plugin registra logs en los siguientes niveles:

- **INFO**: Operaciones exitosas (backup creado, subido a S3)
- **WARNING**: Advertencias (backup deshabilitado, S3 no disponible)
- **ERROR**: Errores (fallo en mysqldump, error de S3)
- **DEBUG**: Información detallada (tamaño de archivos, limpieza)

## 🔄 Flujo de Trabajo

```
1. Hook daily_summary ejecutado
        ↓
2. Verificar si toca backup (frecuencia + hora)
        ↓
3. Ejecutar mysqldump → archivo.sql
        ↓
4. Comprimir con gzip (si habilitado)
        ↓
5. Subir a AWS S3 (si habilitado)
        ↓
6. Eliminar backups antiguos (> retention_days)
        ↓
7. Enviar notificación por email (si configurado)
        ↓
8. Registrar evento en audit_event
```

## 🛡️ Seguridad

- Las credenciales de AWS se almacenan en la configuración JSON del plugin
- Las contraseñas de BD se obtienen de variables de entorno (no se almacenan)
- Los backups pueden ser comprimidos pero no encriptados (usar encriptación de S3 si es necesario)

## 🤝 Integración con Otros Plugins

### email_smtp
Si el plugin `email_smtp` está activo y configurado, el plugin de backup enviará notificaciones automáticamente.

## 🐛 Troubleshooting

### Error: "mysqldump no encontrado"
Asegúrate de tener MySQL client instalado en el sistema.

### Error: "Acceso denegado a S3"
Verifica que las credenciales de AWS sean correctas y tengan permisos de escritura en el bucket.

### Backups no se ejecutan automáticamente
- Verifica que el plugin esté activo: `GET /api/plugins/{id}/estado`
- Revisa los logs de aplicación
- Asegúrate de que el hook `daily_summary` se esté disparando

## 📄 Licencia

MIT License - 3F Team 2026
