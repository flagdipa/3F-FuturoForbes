# Spec Delta: Bóveda Digital (Vault)

## Capabilities

1. **Selección de Directorio (Custom Folder Placement):**
   - El sistema permitirá al usuario no solo subir un archivo, sino asignar o elegir virtual/realmente en qué sub-carpeta se guarda físicamente en el servidor o S3.
   
2. **Auto-Renombrado Estricto:**
   - Todo archivo depositado que cruce el API `/vault` o `/attachments` debe ser interceptado y renombrado bajo la plantilla obligatoria:
     `YYMMDD_hhmm_<origen>_<destino_o_benef>.<extensión>`
   - Para esto, en la capa API se extraen los campos `code` de la cuenta de origen (`Account.code`) y de la cuenta destino o del `Beneficiary.code`.

## Data Models

### Attachment (Actualización)
```diff
 class Attachment(SQLModel, table=True):
     id: int = Field(default=None, primary_key=True)
     entity_type: str
     entity_id: int
-    filename: str
+    original_filename: str # Conservar el nombre viejo por trazabilidad
+    generated_filename: str # El nuevo nombre estructurado YYMMDD_hhmm_...
-    file_path: str
+    file_path: str # Guardar la ruta exacta completa
+    directory_id: Optional[int] = None # Opcional: Liga a una abstracción de Folder
     mime_type: str
```

## API Endpoints (`/api/v1/vault`)

El payload `POST` para inyectar recursos ahora acepta opcionalmente la ruta/dirección dictaminada, así como los punteros o resoluciones relativas al origen y destino, de modo que el backend arme el timestamp string dinámicamente y persista el nombre estructurado final.
