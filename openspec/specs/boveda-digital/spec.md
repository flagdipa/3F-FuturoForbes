# Spec: Bóveda Digital (Vault)

## Goal
Lugar seguro e integrado de almacenamiento digital, que actúa de forma polimórfica para ligar comprobantes (facturas, contratos) a cualquier otra entidad de 3F (cuentas, presupuestos, items de activos).

## Capabilities
1. **Selección de Directorio (Custom Folder Placement):** Asignación de en qué sub-carpeta física se guarda el archivo elegido al vuelo mediante UI.
2. **Auto-Renombrado Estricto:** Generación de nombres de archivo estandarizados con el formato `YYMMDD_hhmm_<origin_code>_<destination_code_or_beneficiary>.<ext>`.
3. **Gestión de Directorios:** Estructura jerárquica de carpetas para organizar los archivos adjuntos.

## Data Models
### Directory & Attachment
```python
class Directory(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    name: str
    parent_id: Optional[int] = Field(default=None, foreign_key="directory.id")
    path: str # Path relativo calculado

class Attachment(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    directory_id: Optional[int] = Field(default=None, foreign_key="directory.id")
    original_filename: str
    generated_filename: str # Formato: YYMMDD_hhmm_ORIG_DEST.ext
    file_path: str
    entity_type: Optional[str] # Ej: 'account', 'payee'
    entity_id: Optional[int]
    mime_type: Optional[str]
```

## API Endpoints (`/api/v1/vault` y `/attachments`)
- `GET /vault/directories` - Listar directorios.
- `POST /vault/directories` - Crear directorio.
- `POST /vault/upload` - Subida de archivos con auto-renombrado.
- `GET /vault/attachments` - Listar metadatos de archivos.
