# Proposal: Standardize State Variable Naming to English

## Problem
The project currently has a mix of Spanish and English variable names, especially within the Alpine.js state stores (e.g., `id_categoria`, `nombre_categoria`, `id_padre`). This inconsistency leads to confusion during development, makes the code harder to maintain, and complicates integration with APIs that use English field names (like the `Payee` model recently updated).

## Proposed Change
Audit and rename all state variables, model fields, and API parameters to use English. This will ensure consistency across the entire stack (Frontend, API, and Database).

### Key Areas to Address
- **Alpine.js Stores:** Update `catForm`, `mergeData`, `benefForm`, `benefManager`, etc.
- **Frontend Templates:** Update all HTML files using these variables in `x-model`, `x-text`, etc.
- **Backend Models:** Finalize the transition of any remaining Spanish fields in `models_v2.py`.
- **API Schemas & Endpoints:** Update Pydantic schemas and FastAPI route parameters.

## Impact
- **Consistency:** High. The entire project will follow a single naming convention.
- **Maintainability:** Improved. Developers won't have to guess which language a variable uses.
- **Coherence:** Better alignment between the frontend state and the backend data structures.

## Scope
- `frontend/static/js/*.js`
- `frontend/templates/*.html`
- `backend/models/*.py`
- `backend/api/v1/*.py`
