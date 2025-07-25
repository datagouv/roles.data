# Architecture Technique de rôles.data.gouv.fr

## Vue d'ensemble

**rôles.data.gouv.fr** est un **système de gestion des rôles et permissions** construit avec **FastAPI** et **PostgreSQL**, conçu pour l'intégration avec les services de l’administration française via **ProConnect**.

## Architecture et concepts clefs

L'applicatif peut être découpé en deux parties :

- **API** : le coeur de l'application, qui permet à des fournisseurs de services, munis d’un `client_id` et d’un `client_secret` (OAuth2) de créer, mettre à jour et utiliser **rôles.data.gouv.fr**.
- **L’interface web** : réservés aux administrateurs (membres de la DINUM) de rôles.data.gouv.fr. Permet d’effectuer des actions exceptionnelles (nommer un admin, reset ou créer un compte de service etc.)

### Stack et partis pris

- Framework : **FastAPI**
- Templating **Jinja2** pour garder une stack simple et éviter d'ajouter une SPA et une chaine de build dédiée
- **HTMX** pour permettre des actions dynamique côté client si nécessaire
- Utilisation du **DSFR**
- **Pattern Repository** pour la couche d'accès aux données
- **Injection de dépendances** pour les services et sessions de base de données
- Documentation **OpenAPI** automatique
- **Modèles Pydantic** pour la validation des requêtes/réponses
- Code **async-first**

### **Authentification et Autorisation**

API :

- **Authentification OAuth2** pour l'accès API
- stockage du `client_secret` dans la DB sous forme de hash. Impossible d'y accèder à nouveau après sa création

Web :

- **SSO ProConnect** avec whitelisting des administrateurs de rôles.data.gouv.fr
- **Middleware de session** pour stocker la session après la ProConnexion

## Structure du Projet

```
db/
├── initdb/           # Creation du shcema de la DB
├── migrations/       # Migrations de la DB
├── seed/             # Initialisation de la DB
├── scripts/          # Script appelés par le point d'entré
└── entrypoint.sh     # Point d’entré docker

src/
├── middleware/       # Middleware personnalisé (auth, etc.)
├── tests/            # Tests d’intégration et units tests
├── utils/            # Utilitaires partagés
│
├── routers/          # Routers
│   ├── auth/         # auth (ProConnect et OAuth2)
│   ├── admin/        # Spécifique interface d’admin
│   └── ...           # routers de l’API REST
├── services/         # Logique métier
│   ├── admin/        # Spécifique interface d’admin
│   └── ...           # services de l’API REST
├── repositories/     # Accès aux données
│   ├── admin/        # Spécifique interface d’admin
│   └── ...           # repositories de l’API REST
│
├── models.py         # Modèles et schémas Pydantic
├── config.py         # Chargement des variables d’env
├── database.py       # Connection à la base de donnée
├── documentation.py  # Config openAPI
```

NB: l’application principale est bien l'API. L'interface d’admin est isolée dans des dossiers `/admin`. Les repositories et les services de l’interface d’admin sont intentionnellement différents de ceux de l’API, pour éviter une contamination entre les deux.

## Commencer

1. Instructions pour (lancer l'app en local)[README.md]
2. Documentation API disponible sur `/docs` (Swagger UI)
3. Interface admin sur `/admin` (nécessite authentification ProConnect)
4. Toutes les opérations admin nécessitent un email super admin dans les paramètres
