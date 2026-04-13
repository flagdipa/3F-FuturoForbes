# Project Structure

```text
/
├── backend/                # Backend FastAPI Application
│   ├── api/                # API Routers
│   │   ├── v1/             # Versioned API logic
│   │   ├── auth/           # Authentication logic
│   │   └── ui_router.py    # Main UI page routing
│   ├── core/               # Core system logic (database, security, etc.)
│   ├── database/           # DB session and initialization
│   ├── migrations/         # Alembic migration scripts
│   ├── models/             # SQLModel/SQLAlchemy data models
│   ├── plugins/            # System plugins/modules
│   ├── tests/              # Backend unit/integration tests
│   └── main.py             # Application entry point
├── frontend/               # Frontend Assets and Templates
│   ├── static/             # Static files (CSS, JS, Images)
│   │   ├── css/            # Stylesheets (neon-3f.css, etc.)
│   │   ├── js/             # UI Logic (Alpine.js stores, managers)
│   │   └── img/            # Static images and icons
│   ├── templates/          # Jinja2 HTML templates
│   │   ├── accounts/       # Account-specific views
│   │   ├── reports/        # Report views
│   │   ├── modals/         # Reusable modal fragments
│   │   └── base.html       # Shared layout
│   └── tests/              # Playwright E2E tests
├── docs/                   # Project documentation
├── scripts/                # Utility scripts (install, backup, etc.)
├── uploads/                # Dynamic user uploads (Vault)
├── .agent/                 # Agent-specific workflows and skills
├── .planning/              # Project planning and codebase mapping
└── requirements.txt        # Python dependencies
```
