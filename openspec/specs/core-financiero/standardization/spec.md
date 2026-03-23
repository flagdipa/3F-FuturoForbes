# Spec: Naming Standardization

## Goal
Enforce English naming conventions across all layers of the 3F system to ensure consistency, clarity, and ease of maintenance.

## Naming Conventions

### 1. Database & Models
- **Primary Keys:** Always `id`.
- **Foreign Keys:** `entity_id` (e.g., `user_id`, `category_id`).
- **Timestamps:** `created_at`, `updated_at`, `deleted_at`.
- **String Fields:** `name`, `description`, `code`, `notes`.
- **Booleans:** `is_active`, `is_admin`, `is_reconciled`.
- **Numeric Fields:** `amount`, `balance`, `rate`.

### 2. API Routes & Schemas
- **Routes:** Plural English nouns (e.g., `/api/v1/accounts`, `/api/v1/categories`).
- **Schemas:** PascalCase for Pydantic (e.g., `CategoryResponse`).
- **JSON keys:** snake_case (e.g., `parent_id`, `current_balance`).

### 3. Frontend (Alpine.js & Templates)
- **Stores:** snake_case for properties (matching API response).
- **Template variables:** snake_case (e.g., `x-text="item.name"`).
- **Global objects:** CamelCase (e.g., `CurrencyUtils`, `NotificationManager`).

## Mapping Legacy to Standard

| Legacy (Spanish) | Standard (English) |
| :--- | :--- |
| `id_categoria` | `id` |
| `nombre_categoria` | `name` |
| `id_padre` | `parent_id` |
| `notas` | `notes` |
| `id_cuenta` | `id` |
| `nombre_cuenta` | `name` |
| `tipo_cuenta` | `type` |
| `monto` | `amount` |
| `fecha` | `date` |
| `id_beneficiario` | `id` |
| `nombre_beneficiario` | `name` |
| `activo` / `activo_p` | `is_active` |

## Remediation Plan
1. **Frontend JS:** Update `category-manager.js`, `transaction-form.js`, `sidebar-manager.js`, etc.
2. **Frontend HTML:** Update all `.html` templates.
3. **Backend API:** Update `backend/api/retro.py` to stop re-mapping to Spanish, eventually phasing it out.
4. **Backend Models:** Update any remaining Spanish fields in `models_v2.py` (e.g., `Plugin` fields).
