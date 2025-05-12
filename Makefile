start:
	uv run fastapi dev src/main.py

test:
	uv run python -m pytest -s src/tests/integration/

lint:
	python -m ruff check .

db_scripts:
	POSTGRES_PASSWORD='d-roles' POSTGRES_HOST='localhost' POSTGRES_PORT='5432' POSTGRES_USER='d-roles' POSTGRES_DB='d-roles' POSTGRES_SCHEMA='d_roles' sh ./db/entrypoint.sh
