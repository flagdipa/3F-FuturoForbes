# Guía de Configuración de PostgreSQL

## Opción 1: PostgreSQL Local

### Instalación en Windows

1. **Descargar PostgreSQL**
   - Ir a: https://www.postgresql.org/download/windows/
   - Descargar el instalador
   - Ejecutar e instalar (recordar la contraseña de postgres)

2. **Crear Base de Datos**

```bash
# Abrir psql o pgAdmin
psql -U postgres

# Crear base de datos
CREATE DATABASE futuroforbes_db;

# Verificar
\l
```

3. **Configurar .env**

```bash
cd backend
cp .env.template .env
```

Editar `.env`:
```
DATABASE_URL=postgresql://postgres:TU_PASSWORD@localhost:5432/futuroforbes_db
```

4. **Ejecutar Script SQL**

```bash
# Opción A: Desde psql
psql -U postgres -d futuroforbes_db -f ../database/tablas.sql

# Opción B: Desde pgAdmin
# Abrir pgAdmin → futuroforbes_db → Tools → Query Tool
# Copiar y ejecutar el contenido de tablas.sql
```

---

## Opción 2: Supabase (PostgreSQL en la Nube)

### Configuración

1. **Crear Proyecto en Supabase**
   - Ir a: https://supabase.com
   - Crear cuenta gratuita
   - Crear nuevo proyecto
   - Guardar la contraseña de la base de datos

2. **Obtener Credenciales**
   - En el dashboard de Supabase
   - Ir a: Settings → Database
   - Copiar la Connection String

3. **Configurar .env**

```bash
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
SUPABASE_URL=https://[PROJECT-REF].supabase.co
SUPABASE_KEY=[ANON-KEY]
```

4. **Ejecutar Script SQL**
   - En Supabase Dashboard
   - Ir a: SQL Editor
   - Copiar y ejecutar el contenido de `tablas.sql`

---

## Verificar Conexión

```bash
cd backend
python -c "from core.db import engine; print(engine.url)"
```

---

## Inicializar con Datos de Ejemplo

```bash
cd backend
python init_data.py
```

---

## Comandos Útiles PostgreSQL

### Conectar a la base de datos
```bash
psql -U postgres -d futuroforbes_db
```

### Ver tablas
```sql
\dt
```

### Ver estructura de una tabla
```sql
\d lista_cuentas
```

### Borrar todas las tablas (CUIDADO!)
```sql
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
```

### Backup
```bash
pg_dump -U postgres futuroforbes_db > backup.sql
```

### Restore
```bash
psql -U postgres -d futuroforbes_db < backup.sql
```

---

## Solución de Problemas

### Error: "password authentication failed"
- Verificar contraseña en `.env`
- Verificar que PostgreSQL esté corriendo

### Error: "database does not exist"
```bash
psql -U postgres
CREATE DATABASE futuroforbes_db;
```

### Error: "could not connect to server"
- Verificar que PostgreSQL esté corriendo
- Windows: Services → PostgreSQL → Start

### Ver logs de PostgreSQL
- Windows: `C:\Program Files\PostgreSQL\15\data\log\`

---

## Migrar de SQLite a PostgreSQL

Si ya tienes datos en SQLite:

```bash
# Exportar datos
sqlite3 futuroforbes.db .dump > data.sql

# Limpiar y adaptar el SQL
# (remover comandos específicos de SQLite)

# Importar a PostgreSQL
psql -U postgres -d futuroforbes_db < data.sql
```

---

## Próximos Pasos

1. ✅ Configurar PostgreSQL
2. ✅ Ejecutar `tablas.sql`
3. ✅ Configurar `.env`
4. ✅ Ejecutar `python init_data.py`
5. ✅ Iniciar servidor: `uvicorn main:app --reload`
