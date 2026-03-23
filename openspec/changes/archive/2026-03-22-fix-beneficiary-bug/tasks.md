## 1. Análisis y Preparación

- [x] 1.1 Buscar todos los usos de campos de beneficiario en español en el frontend
- [x] 1.2 Identificar templates HTML que usan el formulario de beneficiarios
- [x] 1.3 Verificar endpoint /api/v1/categories funciona correctamente
- [x] 1.4 Revisar modelo Payee para confirmar campos disponibles

## 2. Actualizar Formulario de Beneficiarios

- [x] 2.1 Cambiar campos del store benefForm de español a inglés (nombre_beneficiario→name, banco→bank_name, etc.)
- [x] 2.2 Agregar campo default_category_id al store benefForm
- [x] 2.3 Agregar campo code al store benefForm (para visualización, se genera automáticamente)
- [x] 2.4 Agregar dropdown de categorías en el formulario HTML
- [x] 2.5 Implementar carga de categorías desde /api/v1/categories al abrir el formulario

## 3. Generación Automática de Código

- [x] 3.1 Implementar función generatePayeeCode(name) en beneficiary-manager.js
- [x] 3.2 Agregar lógica para verificar unicidad del código (reintentar con _2, _3, etc.)
- [x] 3.3 Generar código automáticamente al crear nuevo beneficiario si está vacío
- [x] 3.4 Mostrar el código generado en el formulario (solo lectura o editable)

## 4. Manejo de Campos Extra

- [x] 4.1 Implementar función para serializar campos extra (telefono, direccion, sitio_web) a JSON
- [x] 4.2 Modificar saveItem() para incluir campos extra en el campo notes como JSON
- [x] 4.3 Implementar función para deserializar campos extra desde notes al editar
- [x] 4.4 Actualizar editItem() para extraer telefono, direccion, sitio_web de notes JSON

## 5. Sincronizar Payloads con Backend

- [x] 5.1 Actualizar payload en saveItem() para usar nombres de campos correctos (name, bank_name, etc.)
- [x] 5.2 Agregar default_category_id al payload cuando se selecciona categoría
- [x] 5.3 Asegurar que los campos null/undefined no rompan el backend
- [x] 5.4 Actualizar mapeo de respuesta del backend a campos del store

## 6. Validar Filtrado de Transacciones

- [x] 6.1 Verificar que viewTransactions() usa el campo payee_id correcto
- [x] 6.2 Validar que el endpoint /api/transactions acepta filtro por payee_id
- [x] 6.3 Corregir mapeo de campos de transacción en la respuesta (si es necesario)
- [x] 6.4 Probar filtrado end-to-end: crear beneficiario → crear transacción → filtrar

## 7. Actualizar Listado de Beneficiarios

- [x] 7.1 Mostrar categoría por defecto en el listado (nombre de categoría, no ID)
- [x] 7.2 Agregar columna o badge que indique si tiene categoría asignada
- [x] 7.3 Actualizar filtros del listado si usan campos renombrados

## 8. Testing y Validación

- [x] 8.1 Test: Crear beneficiario con todos los campos
- [x] 8.2 Test: Editar beneficiario y cambiar categoría por defecto
- [x] 8.3 Test: Verificar que campos extra se guardan y recuperan correctamente
- [x] 8.4 Test: Crear transacción y verificar que se filtra por beneficiario
- [x] 8.5 Test: Verificar que código se genera automáticamente y es único
- [x] 8.6 Test: Verificar manejo de errores si backend rechaza payload

## 9. Documentación

- [x] 9.1 Actualizar comentarios en beneficiary-manager.js explicando el mapeo de campos
- [x] 9.2 Documentar en changelog qué campos cambiaron de nombre
- [x] 9.3 Actualizar estado_proyecto.md marcando beneficiarios como funcional
