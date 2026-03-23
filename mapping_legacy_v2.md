# Mapeo de Campos: Legacy V1 → V2

## Tipos de Entidad Financiera (Legacy) → Institution (V2)

### Campos Legacy (tipos_entidad_financiera):
- `id_tipo` (INTEGER) → **Eliminar** (no se necesita ID separado)
- `nombre_tipo` (VARCHAR) → `Institution.type` (ej: "Bancos", "Billeteras Virtuales")
- `descripcion` (VARCHAR) → **Eliminar** (no equivalente en V2)
- `icono` (VARCHAR) → `Institution.icon` (ej: "fa-university", "fa-wallet")
- `color` (VARCHAR) → **Integrar en tema CSS** (V2 usa sistema de temas)
- `activo` (BOOLEAN) → `Institution.deleted_at is None` (soft delete)

### Instituciones Financieras (Legacy) → Institution (V2)

### Campos Legacy (identidades_financieras):
- `id_identidad` (INTEGER) → `Institution.id` (INTEGER)
- `nombre` (VARCHAR) → `Institution.name` (VARCHAR)
- `id_tipo` (INTEGER) → `Institution.type` (VARCHAR) - **¡Cambio importante!**
- `sucursal` (VARCHAR) → `Institution.branch` (VARCHAR)
- `direccion` (VARCHAR) → `Institution.address` (VARCHAR)
- `web` (VARCHAR) → `Institution.website` (VARCHAR)
- `contacto` (VARCHAR) → `Institution.contact` (VARCHAR)
- `telefono` (VARCHAR) → `Institution.phone` (VARCHAR)
- `cuit` (VARCHAR) → `Institution.cuit` (VARCHAR) - **Mantener igual**
- `logo_url` (VARCHAR) → `Institution.icon` (VARCHAR) - **Reutilizar campo**
- `activo` (BOOLEAN) → `Institution.deleted_at is None` (soft delete)

## Cambios Importantes

### 1. Relación de Tipo → Campo Directo
**Legacy:** Tabla separada `tipos_entidad_financiera` + foreign key `id_tipo`
**V2:** Campo directo `Institution.type` (string) - más simple y eficiente

### 2. Soft Delete vs Boolean Activo
**Legacy:** Campo booleano `activo`
**V2:** Soft delete con `deleted_at` - patrón estándar V2

### 3. Estructura Simplificada
**Legacy:** 2 tablas relacionadas
**V2:** 1 tabla unificada - menos joins, mejor performance

## Datos de Seed (Ejemplo)

### Legacy (V1):
```python
{
    "nombre_tipo": "Bancos", 
    "descripcion": "Entidades bancarias comerciales",
    "icono": "fa-university", 
    "color": "#0d6efd"
}
```

### V2:
```python
{
    "name": "Banco Santander",
    "type": "Bancos",
    "icon": "fa-university",
    "branch": "Sucursal Centro",
    "website": "https://www.santander.com.ar"
}
```

## Endpoints Afectados

1. `GET /financial-entities/types` → Devolver lista de tipos únicos
2. `GET /financial-entities/institutions` → Filtrar por `type`
3. `POST/PUT /financial-entities/types` → **Eliminar** (tipos ahora son strings)
4. `POST/PUT /financial-entities/institutions` → Usar campo `type`
5. `/financial-entities/seed` → Crear instituciones directamente

## Notas de Implementación

- **No hay datos que migrar** (tablas vacías)
- **Frontend compatibility**: Mantener misma estructura de respuesta
- **Performance**: Mejorada al eliminar joins
- **Simplicidad**: Menos código, menos tablas, menos complejidad