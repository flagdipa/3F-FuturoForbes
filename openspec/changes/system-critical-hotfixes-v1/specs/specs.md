# Specs: System Critical Hotfixes V1

## BDD Requirements

### Requirement: Reparar Layout Navbar Tools
- **GIVEN** que existe una barra de herramientas en `base.html` y el código no incluye la etiqueta especial de Bootstrap/AdminLTE para el parent del Dropdown
- **WHEN** el usuario hace click en el botón de la Llave Francesa (🔧)
- **THEN** un menú flotante sobrepuesto se despliega correctamente sin de-estructurar las otras columnas
- **AND** los elementos internos no desplazan visualmente ningún bloque de contenido colindante

### Requirement: Activación precisa de Modales
- **GIVEN** la interfaz activa y los modals ocultos pre-cargados
- **WHEN** un usuario pinche "Gestión de Beneficiarios" u "Categorías" del sub-menú ya reparado
- **THEN** se emitirá el evento Javascript `window.dispatchEvent(...)` al listener correcto exacto que instanció Alpine
- **AND** una Modal inmersiva y oscura del administrador invocado surge en el dashboard, permitiendo interacciones CRUD nativas

### Requirement: Purga Final de Antiguo Motor IA & Mockup
- **GIVEN** el endpoint desactualizado `/api/v1/ia.py` de FastAPI
- **WHEN** un servicio frontal trate de inquirir datos heurísticos en `/forecast` o `/insights` 
- **THEN** ya no debe buscar en su estructura un paquete global de Gemini.
- **AND** responderá limpiamente una lista de diccionarios de ejemplos fijos con "Status: Offline/Mock Data" y un array neutro válido.
- **AND** su script original obsoleto (`backend/core/ia_engine.py`) dejará de existir. No se permite rastro residual de esta dependencia técnica fallida.
