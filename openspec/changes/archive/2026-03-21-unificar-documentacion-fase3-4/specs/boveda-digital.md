# Spec: Bóveda Digital (Vault)

## Goal
Lugar seguro e integrado de almacenamiento digital, que actúa de forma polimórfica para ligar comprobantes (facturas, contratos) a cualquier otra entidad de 3F (cuentas, presupuestos, items de activos).

## Data Models
### Attachment
```python
class Attachment(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    entity_type: str # Ej: 'transaction', 'account'
    entity_id: int # PK de la entidad ligada
    filename: str
    file_path: str # Path seguro en host local o s3
    mime_type: str
```

## API Endpoints (`/api/v1/vault` y `/attachments`)
- `GET /vault` - Repositorio unificado aislado.
- `POST /vault` - Subida encriptada (AES-256 en fs u objeto).
- `POST /attachments` - Endpoint rápido usado por la vista de transacciones para subir tickets.
