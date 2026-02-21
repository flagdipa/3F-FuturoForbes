# FuturoForbes - Actualización a PostgreSQL

## ✅ Cambios Realizados

### 1. Configuración Actualizada

**Archivos modificados:**
- ✅ `backend/.env.template` - Configuración para PostgreSQL
- ✅ `backend/core/config.py` - Default a PostgreSQL
- ✅ `backend/core/db.py` - Pool de conexiones PostgreSQL
- ✅ `database/tablas.sql` - Esquema completo copiado

### 2. Nuevas Características

**PostgreSQL Features:**
- Pool de conexiones (5 conexiones base, 10 overflow)
- Pre-ping para verificar conexiones
- Soporte para JSONB (auditoría)
- Índices optimizados
- Triggers y funciones

---

## 🚀 Pasos para Iniciar

### Paso 1: Instalar PostgreSQL

**Windows:**
```bash
# Descargar de: https://www.postgresql.org/download/windows/
# O usar Supabase (cloud): https://supabase.com
```

### Paso 2: Crear Base de Datos

```bash
# Conectar a PostgreSQL
psql -U postgres

# Crear base de datos
CREATE DATABASE futuroforbes_db;

# Salir
\q
```

### Paso 3: Ejecutar Esquema SQL

```bash
# Ejecutar el esquema completo
psql -U postgres -d futuroforbes_db -f database/tablas.sql
```

### Paso 4: Configurar Variables de Entorno

```bash
cd backend
cp .env.template .env
```

Editar `.env` y actualizar la contraseña:
```
DATABASE_URL=postgresql://postgres:TU_PASSWORD@localhost:5432/futuroforbes_db
```

### Paso 5: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 6: Inicializar con Datos de Ejemplo (Opcional)

```bash
python init_data.py
```

### Paso 7: Iniciar Servidor

```bash
uvicorn main:app --reload
```

Abrir: http://localhost:8000

---

## 📊 Esquema de Base de Datos

El archivo `database/tablas.sql` contiene **32 tablas**:

### Categorías Principales:

1. **Seguridad y Usuarios** (3 tablas)
   - `usuarios`
   - `grupos_usuarios`
   - `registros_auditoria`

2. **Catálogos Core** (4 tablas)
   - `divisas`
   - `historial_divisas`
   - `identidades_financieras`
   - `configuraciones`

3. **Clasificación** (2 tablas)
   - `categorias`
   - `etiquetas`

4. **Cuentas y Activos** (3 tablas)
   - `lista_cuentas`
   - `activos`
   - `inversiones_acciones`

5. **Transacciones** (3 tablas)
   - `beneficiarios`
   - `libro_transacciones`
   - `transacciones_divididas`

6. **Presupuestos** (4 tablas)
   - `años_presupuesto`
   - `tabla_presupuestos`
   - `transacciones_programadas`
   - `presupuesto_division_transacciones`

7. **Automatización** (4 tablas)
   - `grupos_reglas`
   - `reglas_automatizacion`
   - `disparadores_regla`
   - `acciones_regla`

8. **Sistema** (6 tablas)
   - `reportes`
   - `adjuntos`
   - `campos_personalizados`
   - `datos_campos_personalizados`
   - `enlaces_transacciones`
   - `enlaces_etiquetas`

---

## 🔧 Comandos Útiles

### Verificar Conexión
```bash
cd backend
python -c "from core.db import engine; print(engine.url)"
```

### Ver Tablas en PostgreSQL
```bash
psql -U postgres -d futuroforbes_db
\dt
```

### Backup de la Base de Datos
```bash
pg_dump -U postgres futuroforbes_db > backup_$(date +%Y%m%d).sql
```

### Restaurar Backup
```bash
psql -U postgres -d futuroforbes_db < backup_20260129.sql
```

### Reiniciar Base de Datos
```bash
psql -U postgres -d futuroforbes_db
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
\q

psql -U postgres -d futuroforbes_db -f database/tablas.sql
```

---

## 📝 Próximos Pasos

1. ✅ PostgreSQL configurado
2. ✅ Esquema SQL ejecutado
3. 🔄 Actualizar modelos SQLModel para todas las 32 tablas
4. 🔄 Crear endpoints API para todas las funcionalidades
5. 🔄 Implementar frontend AdminLTE4
6. 🔄 Sistema de autenticación
7. 🔄 Motor de reglas automáticas

---

## 🆘 Solución de Problemas

### Error: "password authentication failed"
```bash
# Verificar contraseña en .env
# Verificar que PostgreSQL esté corriendo
```

### Error: "database does not exist"
```bash
psql -U postgres
CREATE DATABASE futuroforbes_db;
```

### Error: "could not connect to server"
```bash
# Windows: Verificar servicio PostgreSQL
services.msc → PostgreSQL → Start
```

---

## 📚 Documentación Adicional

- [POSTGRES_SETUP.md](./POSTGRES_SETUP.md) - Guía detallada de configuración
- [README.md](./README.md) - Documentación principal
- [QUICKSTART.md](./QUICKSTART.md) - Guía de inicio rápido
