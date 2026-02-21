---
name: sistema-3f-architecture
version: "1.0.0"
description: Documentación completa de la arquitectura del Sistema 3f (FuturoForbes). Incluye estructura de directorios, modelos de datos, convenciones de código, endpoints API, y patrones de diseño. Úsalo siempre que trabajes en el sistema 3f.
user-invocable: true
---

# Sistema 3f (FuturoForbes) - Arquitectura y Guía de Desarrollo

## 📋 Visión General

**Sistema**: FuturoForbes - Sistema de Gestión Financiera Personal
**Arquitectura**: FastAPI + SQLModel + MySQL/PostgreSQL + AdminLTE 4
**Versión**: 0.1.0
**Framework**: Sistema 3f (Three-F Framework)

## 🗂️ Estructura de Directorios

```
3f/
├── backend/                          # Backend FastAPI
│   ├── api/                         # Endpoints REST
│   │   ├── __init__.py
│   │   ├── auth.py                  # Autenticación JWT
│   │   ├── cuentas.py              # CRUD de cuentas
│   │   ├── transacciones.py        # CRUD de transacciones
│   │   ├── categorias.py           # CRUD de categorías
│   │   ├── beneficiarios.py        # CRUD de beneficiarios
│   │   ├── programadas.py          # Transacciones programadas
│   │   ├── presupuestos.py         # Presupuestos
│   │   ├── inversiones.py          # Inversiones/acciones
│   │   ├── divisas.py              # Gestión de divisas
│   │   ├── usuarios.py             # Gestión de usuarios
│   │   ├── dashboard.py            # Datos del dashboard
│   │   ├── splits.py               # Transacciones divididas
│   │   ├── configuracion.py        # Configuraciones
│   │   ├── modulos.py              # Sistema de módulos
│   │   ├── fix_db.py               # Herramientas de DB
│   │   └── deps.py                 # Dependencias (auth)
│   │
│   ├── core/                        # Configuración core
│   │   ├── __init__.py             # Exporta settings, engine, init_db, get_session
│   │   ├── config.py               # Settings con pydantic-settings
│   │   ├── db.py                   # Engine MySQL + get_session
│   │   ├── security.py             # JWT, hashing
│   │   └── templates.py            # Configuración Jinja2
│   │
│   ├── models/                      # Modelos SQLModel
│   │   ├── __init__.py             # Exporta todos los modelos
│   │   └── finance.py              # TODOS los modelos en un archivo
│   │
│   ├── plugins/                     # Plugins del sistema
│   │   └── tasas_interes/          # Plugin de tasas de interés (EJEMPLO)
│   │       ├── __init__.py
│   │       ├── models.py
│   │       ├── schemas.py
│   │       ├── README.md
│   │       ├── api/
│   │       │   ├── __init__.py
│   │       │   └── tasas.py
│   │       └── services/
│   │           ├── __init__.py
│   │           └── manual.py
│   │
│   ├── tools/                       # Scripts de utilidad
│   │   ├── migrate_mmex.py
│   │   ├── reset_db.py
│   │   └── ...
│   │
│   └── main.py                      # Punto de entrada FastAPI
│
├── frontend/                        # Frontend AdminLTE 4
│   ├── templates/                  # Plantillas Jinja2
│   │   ├── layouts/                # Layouts base
│   │   │   ├── base.html
│   │   │   └── clean.html
│   │   ├── pages/                  # Páginas
│   │   │   ├── dashboard.html
│   │   │   ├── login.html
│   │   │   ├── register.html
│   │   │   └── profile.html
│   │   └── modules/                # Módulos
│   │       ├── cuentas.html
│   │       ├── transacciones.html
│   │       ├── categorias.html
│   │       ├── beneficiarios.html
│   │       ├── programadas.html
│   │       ├── presupuestos.html
│   │       └── inversiones.html
│   │
│   ├── static/                     # Assets
│   │   ├── dist/                   # AdminLTE 4
│   │   │   ├── css/
│   │   │   ├── js/
│   │   │   └── assets/
│   │   └── js/                     # JS custom
│   │       ├── app_config.js
│   │       ├── filtro_transacciones.js
│   │       └── mdi_manager.js
│   │
│   └── index.html                  # Entry point
│
├── .coordination/                  # Sistema de coordinación
│   ├── README.md
│   ├── current_work.md            # Trabajo actual
│   ├── assigned_tasks.md          # Tareas asignadas
│   ├── completed_work.md          # Trabajo completado
│   ├── conventions.md             # Convenciones del proyecto
│   └── architecture.md            # Referencia rápida de arquitectura
│
└── .agent/                         # Skills del sistema
    └── skills/
        └── sistema-3f-architecture/
            └── SKILL.md           # Este archivo
```

## 🏗️ Arquitectura de 3 Capas

### Capa 1: Modelos (models/finance.py)
- TODOS los modelos SQLModel en un solo archivo
- Definición de tablas, relaciones, enums
- No lógica de negocio aquí

### Capa 2: API (api/*.py)
- Endpoints REST con FastAPI
- Schemas Pydantic inline o importados
- Usa `Depends(get_session)` para DB
- Usa `Depends(get_current_user)` para auth

### Capa 3: Core (core/*.py)
- Configuración centralizada
- Conexión a base de datos
- Autenticación y seguridad
- Templates

## 📊 Modelos de Datos Principales

### 1. Usuario (Seguridad)
```python
class Usuario(SQLModel, table=True):
    __tablename__ = "usuarios"
    id_usuario: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password: str
    creado_el: datetime
    actualizado_el: datetime
    bloqueado: bool = Field(default=False)
    rol_id: Optional[int] = None
```

### 2. Divisa (Catálogo)
```python
class Divisa(SQLModel, table=True):
    __tablename__ = "divisas"
    id_divisa: Optional[int] = Field(default=None, primary_key=True)
    nombre_divisa: str = Field(unique=True)
    codigo_iso: str = Field(unique=True)
    simbolo_prefijo: Optional[str] = None
    simbolo_sufijo: Optional[str] = None
    tipo_divisa: str = Field(default="Fiat")
```

### 3. Cuenta (Core)
```python
class Cuenta(SQLModel, table=True):
    __tablename__ = "lista_cuentas"
    id_cuenta: Optional[int] = Field(default=None, primary_key=True)
    nombre_cuenta: str = Field(unique=True)
    tipo_cuenta: str  # Cash, Checking, Term, Credit Card, Investment, Loan, Asset, Shares
    estado: str = Field(default="Open")
    saldo_inicial: Decimal = Field(default=0)
    id_divisa: int = Field(foreign_key="divisas.id_divisa")
    id_identidad: Optional[int] = Field(foreign_key="identidades_financieras.id_identidad")
    cbu: Optional[str] = None
    limite_credito: Optional[Decimal] = None
    tasa_interes: Optional[Decimal] = None
```

### 4. Transacción (Core)
```python
class Transaccion(SQLModel, table=True):
    __tablename__ = "libro_transacciones"
    id_transaccion: Optional[int] = Field(default=None, primary_key=True)
    id_cuenta: int = Field(foreign_key="lista_cuentas.id_cuenta")
    id_cuenta_destino: Optional[int] = Field(default=None, foreign_key="lista_cuentas.id_cuenta")
    id_beneficiario: int = Field(foreign_key="beneficiarios.id_beneficiario")
    codigo_transaccion: str  # Withdrawal, Deposit, Transfer
    monto_transaccion: Decimal
    estado: Optional[str] = None  # None, Reconciled, Void, Follow up, Duplicate
    id_categoria: Optional[int] = Field(default=None, foreign_key="categorias.id_categoria")
    fecha_transaccion: Optional[str] = None
    es_dividida: bool = Field(default=False)
```

### 5. Beneficiario
```python
class Beneficiario(SQLModel, table=True):
    __tablename__ = "beneficiarios"
    id_beneficiario: Optional[int] = Field(default=None, primary_key=True)
    nombre_beneficiario: str = Field(unique=True)
    id_categoria: Optional[int] = Field(default=None, foreign_key="categorias.id_categoria")
    cbu: Optional[str] = None
    banco: Optional[str] = None
    activo: int = Field(default=1)
    patron_busqueda: Optional[str] = Field(default='')
```

### 6. Categoría
```python
class Categoria(SQLModel, table=True):
    __tablename__ = "categorias"
    id_categoria: Optional[int] = Field(default=None, primary_key=True)
    nombre_categoria: str
    activo: int = Field(default=1)
    id_padre: Optional[int] = Field(default=None, foreign_key="categorias.id_categoria")
    color: Optional[str] = None
    icono: Optional[str] = None
```

### 7. Transacción Programada
```python
class TransaccionProgramada(SQLModel, table=True):
    __tablename__ = "transacciones_programadas"
    id_programacion: Optional[int] = Field(default=None, primary_key=True)
    id_cuenta: int = Field(foreign_key="lista_cuentas.id_cuenta")
    id_beneficiario: int = Field(foreign_key="beneficiarios.id_beneficiario")
    codigo_transaccion: str
    monto_transaccion: Decimal
    repeticiones: Optional[int] = None
    fecha_proxima_ocurrencia: Optional[str] = None
```

### 8. Presupuesto
```python
class Presupuesto(SQLModel, table=True):
    __tablename__ = "tabla_presupuestos"
    id_entrada_presupuesto: Optional[int] = Field(default=None, primary_key=True)
    id_año_presupuesto: int = Field(foreign_key="años_presupuesto.id_año_presupuesto")
    id_categoria: int = Field(foreign_key="categorias.id_categoria")
    periodo: str
    monto: Decimal
    activo: int = Field(default=1)
```

### 9. Inversión/Acción
```python
class InversionAccion(SQLModel, table=True):
    __tablename__ = "inversiones_acciones"
    id_accion: Optional[int] = Field(default=None, primary_key=True)
    fecha_compra: str
    nombre_accion: str
    simbolo: Optional[str] = None
    numero_acciones: Optional[Decimal] = None
    precio_compra: Decimal
    precio_actual: Decimal
```

### 10. Módulo (Sistema de Plugins)
```python
class Modulo(SQLModel, table=True):
    __tablename__ = "modulos"
    id_modulo: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True, index=True)
    nombre_display: str
    descripcion: Optional[str] = None
    version: str = Field(default="1.0.0")
    activo: bool = Field(default=False)
    instalado: bool = Field(default=False)
    configuracion: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
```

## 🔌 Convenciones de API

### Estructura de Endpoints
```python
# CRUD Estándar
GET    /api/{recurso}           # Listar (con paginación opcional)
POST   /api/{recurso}           # Crear
GET    /api/{recurso}/{id}      # Obtener uno
PUT    /api/{recurso}/{id}      # Actualizar
DELETE /api/{recurso}/{id}      # Eliminar

# Endpoints existentes:
/api/auth/*              # Autenticación
/api/cuentas/*          # Cuentas
/api/transacciones/*    # Transacciones
/api/categorias/*       # Categorías
/api/beneficiarios/*    # Beneficiarios
/api/programadas/*      # Transacciones programadas
/api/presupuestos/*     # Presupuestos
/api/inversiones/*      # Inversiones
/api/divisas/*          # Divisas
/api/usuarios/*         # Usuarios
/api/dashboard/*        # Dashboard
/api/modulos/*          # Módulos
/api/configuracion/*    # Configuración
/api/splits/*           # Transacciones divididas
/api/tools/*            # Herramientas
/api/tasas-interes/*    # Plugin tasas de interés
```

### Patrón de Endpoints
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from core import get_session  # SIEMPRE usar este import
from models.finance import MiModelo
from api.deps import get_current_user  # Para rutas protegidas

router = APIRouter()

# Listar todos
@router.get("/")
def list_items(
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)  # Opcional
):
    statement = select(MiModelo)
    return session.exec(statement).all()

# Crear
@router.post("/")
def create_item(
    data: MiModeloCreate,
    session: Session = Depends(get_session)
):
    item = MiModelo(**data.dict())
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

# Obtener uno
@router.get("/{item_id}")
def get_item(
    item_id: int,
    session: Session = Depends(get_session)
):
    item = session.get(MiModelo, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="No encontrado")
    return item

# Actualizar
@router.put("/{item_id}")
def update_item(
    item_id: int,
    data: MiModeloUpdate,
    session: Session = Depends(get_session)
):
    item = session.get(MiModelo, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="No encontrado")
    
    for field, value in data.dict(exclude_unset=True).items():
        setattr(item, field, value)
    
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

# Eliminar (soft delete - cambiar activo=False)
@router.delete("/{item_id}")
def delete_item(
    item_id: int,
    session: Session = Depends(get_session)
):
    item = session.get(MiModelo, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="No encontrado")
    
    item.activo = False  # Soft delete
    session.add(item)
    session.commit()
    return {"message": "Eliminado correctamente"}
```

## ⚙️ Configuración (core/config.py)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database - MySQL por defecto
    database_url: str = "mysql+pymysql://root:@localhost:3306/futuroforbes_db"
    
    # Security
    secret_key: str = "your-secret-key-change-this"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: List[str] = ["*"]
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

## 🗄️ Base de Datos (core/db.py)

```python
from sqlmodel import create_engine, Session, SQLModel
from core.config import settings

engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

def init_db():
    """Crear todas las tablas en la base de datos"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency para obtener sesión de base de datos"""
    with Session(engine) as session:
        yield session
```

## 🔐 Autenticación (api/deps.py)

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Retornar usuario o token decodificado
    return payload
```

## 🎨 Frontend (AdminLTE 4)

### Estructura de Templates
```html
<!-- layouts/base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}FuturoForbes{% endblock %}</title>
    <link rel="stylesheet" href="/static/dist/css/adminlte.min.css">
</head>
<body class="hold-transition sidebar-mini">
    <div class="wrapper">
        {% include 'modules/header.html' %}
        {% include 'modules/sidebar.html' %}
        
        <div class="content-wrapper">
            {% block content %}{% endblock %}
        </div>
        
        {% include 'modules/footer.html' %}
    </div>
</body>
</html>

<!-- pages/dashboard.html -->
{% extends "layouts/base.html" %}
{% block content %}
    <h1>Dashboard</h1>
{% endblock %}
```

## 📝 Reglas de Codificación

### 1. Modelos
- Todos los modelos en `models/finance.py`
- Usar `__tablename__` explícito
- Foreign keys con nombres descriptivos
- Relaciones con `back_populates`

### 2. APIs
- Un archivo por recurso en `api/`
- Router con prefijo en `main.py`
- Usar `Depends(get_session)` SIEMPRE
- Schemas Pydantic inline o en archivo separado

### 3. Plugins
- Directorio en `backend/plugins/{nombre_plugin}/`
- Estructura: models.py, schemas.py, api/, services/
- Registrar en main.py
- Agregar modelos a models/__init__.py

### 4. Convenciones de Nombres
- **Tablas**: snake_case, plural (ej: `lista_cuentas`, `libro_transacciones`)
- **Modelos**: PascalCase (ej: `Cuenta`, `Transaccion`)
- **Endpoints**: kebab-case (ej: `/api/tasas-interes`)
- **Variables**: snake_case
- **Enums**: UPPER_SNAKE_CASE

### 5. Soft Delete
- Nunca eliminar registros físicamente
- Usar campo `activo` (int o bool)
- Filtros por defecto: `activo=True`

### 6. Fechas
- Usar `datetime.utcnow()` para timestamps
- Campos de fecha de usuario como `Optional[str]`

### 7. Decimales
- Usar `Decimal` para montos de dinero
- Precisión: `decimal_places=2` o `4` para tasas

### 8. Coordinación
- SIEMPRE leer `.coordination/current_work.md` antes de empezar
- Actualizar `.coordination/assigned_tasks.md` al asignar tarea
- Mover a `.coordination/completed_work.md` al completar
- Seguir `.coordination/conventions.md`

## 🚀 Integración de Nuevos Plugins

### Paso 1: Crear Estructura
```
backend/plugins/{nombre_plugin}/
├── __init__.py
├── models.py
├── schemas.py
├── api/
│   ├── __init__.py
│   └── {nombre}.py
└── services/
    ├── __init__.py
    └── {servicio}.py
```

### Paso 2: Crear Modelos
```python
# plugins/{nombre_plugin}/models.py
from sqlmodel import SQLModel, Field
from typing import Optional

class MiPluginModelo(SQLModel, table=True):
    __tablename__ = "mi_plugin_tabla"
    id: Optional[int] = Field(default=None, primary_key=True)
    # ... campos
```

### Paso 3: Crear Endpoints
```python
# plugins/{nombre_plugin}/api/{nombre}.py
from fastapi import APIRouter, Depends
from sqlmodel import Session
from core import get_session

router = APIRouter(prefix="/{nombre-plugin}", tags=["Nombre Plugin"])

@router.get("/")
def list_items(session: Session = Depends(get_session)):
    pass
```

### Paso 4: Registrar en main.py
```python
# main.py
from plugins.{nombre_plugin}.api import router as {nombre_plugin}_router

app.include_router({nombre_plugin}_router, prefix="/api/{nombre-plugin}", tags=["Nombre Plugin"])
```

### Paso 5: Registrar Modelos
```python
# models/__init__.py
from plugins.{nombre_plugin}.models import MiPluginModelo

__all__ = [
    # ... modelos existentes
    "MiPluginModelo"
]
```

## 🔧 Comandos Útiles

```bash
# Iniciar servidor
cd backend
uvicorn main:app --reload

# Crear migraciones (si se usa Alembic)
alembic revision --autogenerate -m "descripcion"
alembic upgrade head

# Instalar dependencias
pip install -r requirements.txt

# Reset de base de datos
python tools/reset_db.py
```

## 📚 Dependencias Principales

```
fastapi==0.109.0
sqlmodel==0.0.14
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
jinja2==3.1.2
python-dotenv==1.0.0
PyMySQL==1.1.0  # Para MySQL
psycopg2-binary==2.9.9  # Opcional para PostgreSQL
```

## ✅ Checklist de Desarrollo

Antes de crear código nuevo, verificar:
- [ ] ¿El modelo tiene `__tablename__`?
- [ ] ¿Usé `Depends(get_session)` en los endpoints?
- [ ] ¿Implementé soft delete (campo `activo`)?
- [ ] ¿Los montos usan `Decimal`?
- [ ] ¿Las fechas usan `datetime.utcnow()`?
- [ ] ¿Registré el router en main.py?
- [ ] ¿Agregué el modelo a models/__init__.py?
- [ ] ¿Seguí las convenciones de nombres?
- [ ] ¿Leí `.coordination/current_work.md`?
- [ ] ¿Actualicé archivos de coordinación?

## 🐛 Errores Comunes y Soluciones

### Error: "No module named 'core'"
**Solución**: Asegurarte de ejecutar desde `backend/` y que `core/` tenga `__init__.py`

### Error: "Table doesn't exist"
**Solución**: El modelo no está importado en `models/__init__.py`. Agregarlo.

### Error: "Foreign key constraint fails"
**Solución**: Verificar que el ID referenciado existe antes de crear el registro.

### Error: "Decimal overflow"
**Solución**: Aumentar `max_digits` en el campo Decimal del modelo.

## 📞 Referencias Rápidas

- **Config**: `core.config.settings`
- **DB Session**: `core.get_session`
- **Templates**: `core.templates.templates`
- **Auth**: `api.deps.get_current_user`
- **Main App**: `backend/main.py`
- **Models**: `backend/models/finance.py`
- **Coordination**: `.coordination/`

---

**Versión del Skill**: 1.0.0  
**Última actualización**: 2026-02-16  
**Sistema**: FuturoForbes 3f v0.1.0
