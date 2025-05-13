# Include environment variables from .env file
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

start:
	uv run fastapi dev src/main.py

test:
	uv run python -m pytest -s src/tests/integration/

lint:
	python -m ruff check .

db_start:
	docker-compose up

db_scripts:
	echo "Using DB_HOST: ${DB_HOST}, DB_PORT: ${DB_PORT}, etc."
	sh ./db/entrypoint.sh
	DB_PASSWORD='d-roles' DB_PORT='5433' DB_NAME='d-roles' sh ./db/entrypoint.sh
