# Rôles.data.gouv.fr

[![Run Integration Tests](https://github.com/datagouv/d-roles/actions/workflows/integration_tests.yml/badge.svg)](https://github.com/datagouv/d-roles/actions/workflows/integration_tests.yml)
[![Create and deploy a new release](https://github.com/datagouv/d-roles/actions/workflows/create-deploy-release.yml/badge.svg)](https://github.com/datagouv/d-roles/actions/workflows/create-deploy-release.yml)

API de gestion des droits utilisateurs pour les outils du pôle DATA

## Table des matières

- [Installation](#installation)
- [Configuration docker](#configuration-docker)
- [Base de données](#base-de-données)
- [Tests](#tests)
- [Déploiements](#déploiements)
- [Conventions de code](#conventions-de-code)

## Installation

### Prérequis

- Python 3.13+
- [uv](https://docs.astral.sh/uv) - Gestionnaire de dépendances
- PostgreSQL 15.7
- Docker & Docker Compose

### Installation rapide

```bash
# Cloner le dépôt
git clone https://github.com/datagouv/d-roles.git
cd d-roles

# Installer les dépendances
uv sync

# Lancer les conteneurs de base de données
make docker_local

# Initialiser & migrer la base de données
make db_init

# Lancer l'application
make start
```

NB : en mode developpement rapide, l'application n’est pas dockerisée. Seuls les containers de la base de donnée le sont.

## Configuration docker

Pour tester la configuration docker complète de l'application :

```
make docker
```

La commande lance les containers :

- nginx (cf `./nginx.conf`)
- app
- postgres-local
- postgres-test
- smtp-local

Ce mode permet de tester la conf nginx, le dockerfile et la logique de migration.

## Base de données

### environnements

La variable `DB_ENV` est utilisée pour distinguer les différents environnements :

- `local` : developpement local (seedé)
- `test` : CI (seedé)
- `dev` : intégration (seedé)
- `preprod` : environnement iso prod pour tester les migrations et autres opérations de maintenance
- `prod` environnement de production

### local

```
# lancer les DB pour les environnements local et test
docker-compose-up

# se connecter
psql -h localhost -p 5432 -U d-roles -d d-roles

# executer les migrations et la seed
make db_init
```

### Scripts de provisionnement de la base de données

Les scripts appliqués à la base de donnée sont executés dans cet ordre :

- `schema.sql` - creation du schema (uniquement les environnements local, test)
- `create.sql` - création de la base de données
- `migrations/*` - migrations successives
- `seed.sql` - données de tests (uniquement les environnements local, test, dev)

#### Migrations

Ajouter un fichier `db/migrations/{YYYYMMDD}_{description}.sql` avec le SQL nécessaire pour la migration

#### Seed

Mettre a jour le fichier seeds (selon l'environnement) dans `db/seeds/{environnement}/seed.sql`

## Tests

Les tests d'intégration tournent sur pytest. La DB postgres-test est une DB différent de la DB de dev, pré-stubbé et isolée.

```
# démarrer la DB
make docker_local

# test de migrations/seed
# make db_init

# lancer les tests
make test
```

## Déploiements

L'application est déployée sur différents environnements :

- [dev] https://roles.dev.data.gouv.fr : données de test. À utiliser pour en intégration.
- [preprod] https://roles.preprod.data.gouv.fr : à vocation à être iso prod (pull & replace avec les données de prod quotidiennement)
- [prod] https://roles.data.gouv.fr

Les déploiement se font via un message de commit formaté de la manière suivante : [ENV:VERSION].

```
# deploy on roles.dev.data.gouv.fr
make deploy_dev

# deploy on roles.preprod.data.gouv.fr
make deploy_preprod

# deploy on roles.data.gouv.fr
make deploy_prod
```

NB : ces commandes déploient la branche `main` uniquement.

## Conventions de code

### Pre-commit

```
uv add pre-commit
pre-commit install --install-hooks
```

### Formatting et linting

Ce projet utilise Ruff pour le formatage et le linting :

```
make lint
```
