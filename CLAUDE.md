# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Project structure:

- main folders: src (FASTAPI code), db (database code (SQL and Bash)), templates (jinja html templates).

# Development guidelines:

- Follow `README.md` and `CONTRIBUTING.md` (especially regarding testing, linting, formatting).
- Edit existing files rather than creating new ones.

# Review guidelines:

- If asked to review a PR, be constructive and helpful in your feedback. Especially provide feedback on:
  - Code quality and best practices
  - Potential bugs or issues
  - Performance considerations
  - Security concerns
  - Test coverage

## Database

- DB schema changes, also called migrations: modify code first, then `./scripts/alembic revision --autogenerate`, rename file, run `./scripts/alembic upgrade`.
  - Avoid creating multiple revisions in the same PR whenever possible, prefer merging them.
  - Avoid having a `COMMIT` inside a revision at all costs.
- Can restore clean DB with `./scripts/db restore-dump`.

## Testing, linting, formatting

- Ruff is handled by pre-commit hook
- You can launch individual test using `uv run python -m pytest -s src/tests/integration`and fill in the test file name
- Features are available using CLIs:
  - `make test` : run all test suite

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

NEVER use command that start with `make deploy_`
