# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

### Development
- `make start` - Start the development server (FastAPI dev mode)
- `make test` - Run integration tests (uses test database)
- `make lint` - Run Ruff linting and formatting checks
- `uv sync` - Install/sync dependencies using uv package manager

### Database
- `make db_start` - Start PostgreSQL containers (local + test databases)
- `make db_scripts` - Initialize and migrate both local and test databases
- Database connection: `psql -h localhost -p 5432 -U d-roles -d d-roles`

### Docker & Deployment
- `make docker` - Test full Docker configuration (nginx + app + postgres)
- `make deploy_dev` - Deploy to development environment
- `make deploy_preprod` - Deploy to preproduction environment
- `make deploy_prod` - Deploy to production environment

## Architecture Overview

D-Rôles is a **role and permissions management system** built with FastAPI and PostgreSQL, designed for French government services integration via ProConnect.

### Core Components

**Dual Interface Architecture:**
- **API**: OAuth2-secured REST API for service providers with `client_id`/`client_secret`
- **Web Interface**: Admin-only web UI for DINUM administrators using Jinja2 templates + HTMX

**Key Architectural Patterns:**
- Repository pattern for data access layer (`src/repositories/`)
- Service layer for business logic (`src/services/`)
- FastAPI dependency injection for database sessions and services
- Async-first codebase throughout
- Pydantic models for request/response validation

### Directory Structure

```
src/
├── routers/          # FastAPI route handlers (API + web)
│   ├── auth/         # Authentication (ProConnect OAuth2)
│   ├── admin/        # Admin web interface routes
│   └── [entities]    # CRUD routes for users, groups, roles, etc.
├── repositories/     # Data access layer (PostgreSQL queries)
├── services/         # Business logic and external integrations
├── models/           # Pydantic models and validation
├── middleware/       # Custom FastAPI middleware
├── templates/        # Jinja2 templates for web interface
└── tests/
    ├── integration/  # API integration tests
    └── unit/         # Unit tests
```

### Authentication & Authorization

**API Access:**
- OAuth2 Bearer tokens for service-to-service communication
- JWT tokens with configurable expiration (API_ACCESS_TOKEN_EXPIRE_MINUTES)
- Separate secret keys for API (API_SECRET_KEY) and sessions (SESSION_SECRET_KEY)

**Web Interface:**
- ProConnect OAuth2 integration for French government authentication
- Session-based authentication for admin users
- Super admin emails configured via SUPER_ADMIN_EMAILS environment variable

### Database Management

**Environment-based configuration:**
- `local` - Development with seed data
- `test` - CI environment with isolated test database (port 5433)
- `dev` - Integration environment with seed data
- `preprod` - Production-like environment for testing
- `prod` - Production environment

**Migration System:**
1. `db/initdb/create.sql` - Base schema creation
2. `db/migrations/YYYYMMDD_description.sql` - Sequential migrations
3. `db/seed/seed.sql` - Test data (non-production environments only)

### Key Models & Business Logic

**Core Entities:**
- Users (with ProConnect integration via `sub_pro_connect`)
- Service Providers (OAuth2 clients)
- Roles and Groups (hierarchical permissions)
- Organizations (validated via SIRET numbers using Luhn algorithm)

**Validation Features:**
- SIRET validation with Luhn checksum algorithm (`src/model.py:9-35`)
- Email validation using Pydantic EmailStr
- Environment-based secret validation (minimum 32 characters)

### Development Notes

- Python 3.13+ required
- Uses `uv` package manager instead of pip
- Ruff for linting and formatting
- Pre-commit hooks available
- PostgreSQL 15.7+ required
- All database operations are async using `asyncpg`
- Sentry integration for error tracking (optional)

### Testing

Integration tests run against isolated PostgreSQL test database on port 5433. Tests are located in `src/tests/integration/` and follow a specific order (test_0_health.py, test_1_roles.py, etc.).
