# Include environment variables from .env file
ifneq (,$(wildcard ./.env))
    include .env
    export
endif


start:
	uv run fastapi dev src/main.py

test:
	DB_ENV=test uv run python -m pytest -s src/tests/integration/

lint:
	python -m ruff check .

docker: # locally run entire application in docker
	docker compose up smtp-local postgres-local app nginx

docker_local: # only run DB & mail containers
	docker compose up smtp-local postgres-local postgres-test

db_init:
	echo "Using DB_SCHEMA: ${DB_SCHEMA}"
	DB_HOST='localhost' DB_PORT=5432 sh ./db/entrypoint.sh
	DB_HOST='localhost' DB_PASSWORD='d-roles' DB_PORT=5433 DB_NAME='d-roles' sh ./db/entrypoint.sh

deploy_prod:
	git checkout main && \
	SKIP=conventional-pre-commit git commit --allow-empty -m "[www:minor]"  && \
	git push origin main

deploy_dev:
	git checkout main && \
	SKIP=conventional-pre-commit git commit --allow-empty -m "[dev:minor]"  && \
	git push origin main
