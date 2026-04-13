# Technology Stack

## Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (0.109.0)
- **Runtime**: Python 3.x
- **ORM/Data Modeler**: [SQLModel](https://sqlmodel.tiangolo.com/) (0.0.14) based on SQLAlchemy 2.0 and Pydantic v2
- **Database**: 
  - SQLite (Default for local development)
  - PostgreSQL (Supported via `psycopg2-binary`)
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/) (1.13.1)
- **Security**: 
  - `python-jose` (JWT)
  - `passlib` with `bcrypt` (Password hashing)
- **Server**: [Uvicorn](https://www.uvicorn.org/)

## Frontend
- **Templating**: [Jinja2](https://palletsprojects.com/p/jinja/) (Integrated with FastAPI)
- **Library**: [Alpine.js](https://alpinejs.dev/) (v3.13.3) for reactive UI components
- **Styling**: 
  - [Bootstrap 5](https://getbootstrap.com/)
  - [AdminLTE 4](https://adminlte.io/) (Beta 2) for dashboard layout
  - Custom CSS (Neon style)
- **HTTP Client**: [Axios](https://axios-http.com/)
- **Components**:
  - [SweetAlert2](https://sweetalert2.github.io/) for alerts/modals
  - [FontAwesome 6](https://fontawesome.com/) for icons
  - [SortableJS](https://sortablejs.com/) for drag-and-drop

## Testing
- **E2E Testing**: [Playwright](https://playwright.dev/)
- **Backend Testing**: [Pytest](https://docs.pytest.org/)
