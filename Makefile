start:
	uv run fastapi dev src/main.py

test:
	uv run python -m pytest -s src/tests/integration/

lint:
	python -m ruff check .

docker: # run application in docker
	docker-compose up

db_start: # only run DB container
	docker-compose up -d postgres-dev postgres-test

db_scripts: # run creation, migration, and seed scripss
	POSTGRES_PASSWORD='d-roles' POSTGRES_HOST='localhost' POSTGRES_PORT='5432' POSTGRES_USER='d-roles' POSTGRES_DB='d-roles' POSTGRES_SCHEMA='d_roles' sh ./db/entrypoint.sh
