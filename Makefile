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

docker: # run application in docker
	docker-compose up

db_scripts:
	echo "Using DB_SCHEMA: ${DB_SCHEMA}"

	DB_HOST='localhost' DB_PORT=5432 sh ./db/entrypoint.sh
	DB_HOST='localhost' DB_PASSWORD='d-roles' DB_PORT=5433 DB_NAME='d-roles' sh ./db/entrypoint.sh

db_start: # only run DB container
	docker-compose up postgres-dev postgres-test
