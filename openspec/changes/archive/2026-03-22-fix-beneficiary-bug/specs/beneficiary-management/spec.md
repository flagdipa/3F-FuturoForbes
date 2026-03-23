## ADDED Requirements

### Requirement: Sincronización de campos entre frontend y backend
El sistema SHALL asegurar que los campos del beneficiario en el frontend coincidan con los del modelo del backend.

#### Scenario: Crear beneficiario con campos correctos
- **WHEN** el usuario crea un nuevo beneficiario desde el frontend
- **THEN** el sistema envía los campos: name, code, default_category_id, bank_name, cbu, cuit, notes
- **AND** el frontend no envía campos inexistentes en el backend (sitio_web, telefono, direccion)

#### Scenario: Editar beneficiario existente
- **WHEN** el usuario edita un beneficiario existente
- **THEN** el sistema actualiza solo los campos válidos del modelo Payee
- **AND** los campos extra (telefono, direccion, sitio_web) se almacenan en el campo notes como metadata JSON

### Requirement: Generación automática de código de beneficiario
El sistema SHALL generar automáticamente el campo code para nuevos beneficiarios basado en su nombre.

#### Scenario: Crear beneficiario sin código explícito
- **WHEN** el usuario crea un beneficiario sin especificar el código
- **THEN** el frontend genera el código usando: nombre.toLowerCase().replace(/[^a-z0-9]/g, '_').substring(0, 20)
- **AND** si el código ya existe, se agrega un número incremental al final

#### Scenario: Crear beneficiario con código duplicado
- **WHEN** el usuario crea un beneficiario cuyo código generado ya existe
- **THEN** el sistema intenta con: code_2, code_3, etc. hasta encontrar uno único
- **AND** el sistema guarda el beneficiario con el código único generado

### Requirement: Gestión de categoría por defecto
El sistema SHALL permitir asignar una categoría por defecto a cada beneficiario para auto-categorización.

#### Scenario: Asignar categoría por defecto al crear beneficiario
- **WHEN** el usuario crea un beneficiario y selecciona una categoría por defecto
- **THEN** el sistema almacena el default_category_id en el beneficiario
- **AND** el sistema muestra el nombre de la categoría en el listado de beneficiarios

#### Scenario: Modificar categoría por defecto
- **WHEN** el usuario edita un beneficiario y cambia su categoría por defecto
- **THEN** el sistema actualiza el campo default_category_id
- **AND** las transacciones futuras usan la nueva categoría por defecto

#### Scenario: Mostrar dropdown de categorías
- **WHEN** el usuario abre el formulario de creación/edición de beneficiario
- **THEN** el sistema carga las categorías disponibles del usuario desde /api/v1/categories
- **AND** muestra un dropdown con las categorías ordenadas alfabéticamente
- **AND** incluye opción "Sin categoría" para dejar el campo vacío

### Requirement: Manejo de campos extra en notes
El sistema SHALL almacenar campos no existentes en el modelo (telefono, direccion, sitio_web) dentro del campo notes como JSON.

#### Scenario: Guardar campos extra al crear beneficiario
- **WHEN** el usuario ingresa telefono, direccion o sitio_web en el formulario
- **THEN** el frontend serializa estos campos en JSON: {"telefono": "...", "direccion": "...", "sitio_web": "..."}
- **AND** el sistema almacena el JSON en el campo notes del beneficiario

#### Scenario: Recuperar campos extra al editar beneficiario
- **WHEN** el usuario edita un beneficiario que tiene campos extra en notes
- **THEN** el sistema parsea el campo notes como JSON
- **AND** extrae telefono, direccion y sitio_web para mostrarlos en el formulario
- **AND** si notes no es JSON válido, se muestra como notas simples

## MODIFIED Requirements

(No hay capabilities existentes que requieran modificación - estos son nuevos requisitos para funcionalidad existente)
