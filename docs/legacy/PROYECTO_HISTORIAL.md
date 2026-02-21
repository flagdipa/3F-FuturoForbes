# FuturoForbes - Historial del Proyecto y Requerimientos

Este documento detalla la evolución del sistema, desde su concepción basada en Money Manager Ex (MMEX) hasta su estado actual como una plataforma de gestión financiera futurista.

## 📜 Visión General
FuturoForbes nace con la necesidad de tener un sistema de finanzas personales robusto, modular y visualmente impactante, heredando la potencia de MMEX pero con una interfaz moderna y tecnología web de última generación.

---

## 🚀 Fases y Milagros

### Fase 1: Cimentación y Análisis MMEX
*   **Análisis de MMEX:** Extracción de la lógica de negocio y esquema de base de datos de Money Manager Ex.
*   **Traducción y Localización:** Adaptación de términos financieros al español y contexto regional.
*   **Esquema Unificado:** Creación de una base de datos optimizada de 25+ tablas cubriendo cuentas, transacciones, inversiones, beneficiarios, presupuestos, etc.

### Fase 2: Backend Core (FastAPI + SQLModel)
*   **Autenticación:** Implementación de JWT para seguridad robusta.
*   **Motores de DB:** Soporte inicial para MySQL y migración hacia PostgreSQL para mayor escalabilidad.
*   **API RESTful:** Desarrollo de endpoints modulares para todas las entidades financieras.
*   **Precisión Financiera:** Evolución de tipos de datos `float` hacia `Decimal` para evitar errores de redondeo.

### Fase 3: Frontend y Diseño Futurista
*   **AdminLTE 4:** Adopción del framework UI base, personalizado con CSS avanzado.
*   **Tema Neón Futurista:** Creación de una identidad visual única con colores vibrantes y efectos de brillo.
*   **DataTables Pro:** Integración de tablas interactivas para gestión masiva de datos.

### Fase 4: Módulos Especializados
*   **Inversiones y Stocks:** Gestión de portafolio con seguimiento de precios y ganancias.
*   **Transacciones Divididas (Splits):** Capacidad de repartir un gasto en múltiples categorías.
*   **Transacciones Programadas:** Automatización de registros recurrentes.
*   **Beneficiarios:** Registro detallado de entidades y personas asociadas a movimientos.

---

## 🛠 Requerimientos Implementados vs. Pendientes

### ✅ Implementado (Core & Beta Final)
*   [x] Registro y Autenticación de Usuarios.
*   [x] Gestión de Cuentas (Bancarias, Efectivo, Tarjetas).
*   [x] Libro de Transacciones Completo.
*   [x] Árbol de Categorías Jerárquico.
*   [x] Soporte Multi-divisa con tasas de conversión.
*   [x] Dashboard con estadísticas clave.
*   [x] Sistema de Configuración Persistente.
*   [x] **Inversiones & Stocks:** Portafolio detallado con Decimal precision.
*   [x] **Drag-and-Drop:** Reordenamiento de columnas persistente.
*   [x] **Precisión Total:** Migración completa a `Decimal`.



### ⏳ Pendiente (Road to Release 1.0)
*   [ ] Importación CSV/MMEX automatizada.
*   [ ] Reportes Avanzados exportables (PDF/Excel).
*   [ ] Multi-usuario (Cuentas compartidas).

---

## 🗝 Necesidades Críticas Detectadas
1.  **Navegación Tradicional:** El sistema utiliza navegación de página completa para mejor compatibilidad y simplicidad.
2.  **Integridad de Datos:** No se permiten discrepancias en centavos (solucionado vía Decimal).
3.  **Identidad Visual:** El sistema debe sentirse "Premium" y "Vanguardista".

**Última Actualización:** 31 de Enero, 2026.
