# Testing Strategy

## E2E Testing (Frontend)
- **Tool**: [Playwright](https://playwright.dev/)
- **Location**: `frontend/tests/`
- **Scope**: User flows, complex UI interactions (modals, drag-and-drop), and multi-step processes like transaction splitting.
- **Reporting**: Generates HTML and JSON reports (`frontend/playwright-report/`).

## Backend Testing
- **Tool**: [Pytest](https://docs.pytest.org/)
- **Location**: `backend/tests/`
- **Scope**:
  - API endpoint verification.
  - Ledger calculation integrity.
  - Plugin hook registration.
  - Authentication and permissions.

## Execution
- **Frontend**: `cd frontend && npm test`
- **Backend**: `cd backend && pytest`
