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
	uv ruff check .

format:
	uv ruff format .

docker: # run application in docker
	docker compose up postgres-local app nginx

db_scripts:
	echo "Using DB_SCHEMA: ${DB_SCHEMA}"
	DB_HOST='localhost' DB_PORT=5432 sh ./db/entrypoint.sh
	DB_HOST='localhost' DB_PASSWORD='d-roles' DB_PORT=5433 DB_NAME='d-roles' sh ./db/entrypoint.sh

db_start: # only run DB container in background with logging
	docker compose up -d postgres-local postgres-test > db_startup.log 2>&1
	@echo "Database containers started in background. Check 'db_startup.log' for startup logs."
	@echo "Use 'docker compose logs postgres-test postgres-local' to follow logs."

db_stop: # stop DB containers
	docker compose down

db_logs: # show database logs
	docker compose logs postgres-test postgres-local

db_status: # check database container status
	docker compose ps postgres-test postgres-local

deploy_prod:
	git checkout main && \
	SKIP=conventional-pre-commit git commit --allow-empty -m "[www:minor]"  && \
	git push origin main

deploy_preprod:
	git checkout main && \
	SKIP=conventional-pre-commit git commit --allow-empty -m "[preprod:minor]"  && \
	git push origin main

deploy_dev:
	git checkout main && \
	SKIP=conventional-pre-commit git commit --allow-empty -m "[dev:minor]"  && \
	git push origin main
