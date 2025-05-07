# D-roles

Gestion des droits des utilisateurs des outils du pôle DATA

## Developpement

### Applicatif

Le projet s’appuie sur [uv](https://docs.astral.sh/uv) pour la gestion des dépendances.

```
uv sync
uv run fastapi dev src/main.py
```

Pour build le container applicatif

```
docker build .
docker images
docker run -d -p 8888:80 --name d-roles-applicatif <Image-ID>
```

### DB

Local dev

```
docker-compose-up
psql -h localhost -p 5432 -U d-roles -d d-roles
```

## Code conventions

### Pre-commit

Ce projet a un hook pre-commit

```
uv add pre-commit
pre-commit install --install-hooks
```

### Lint and format code

To lint, format and sort imports, this repository uses Ruff. You can run the following command to lint and format the code:

```
uv run ruff check --fix && uv run ruff format
```

### Tests

```
uv run python -m pytest -s src/tests/integration
```

### Bonnes pratiques

- [Design patterns](https://medium.com/@lautisuarez081/fastapi-best-practices-and-design-patterns-building-quality-python-apis-31774ff3c28a)
- [Bonnes pratiques de code](https://github.com/zhanymkanov/fastapi-best-practices)
