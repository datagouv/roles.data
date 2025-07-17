api_summary = "Cette API REST permet à un fournisseur de service (typiquement, une startup d’état) de déléguer des droits d’accès à ses utilisateurs."

api_description = """
Par exemple, l’utilisateur *john-doe@numerique.gouv.fr* obtient les droits d’accès en écriture à ma-startup-d-etat.fr. Son groupe est créé dans d-rôles, avec le scope `ecriture`. *john-doe@numerique.gouv.fr* est ajouté au groupe avec le rôle `administrateur`.

En tant qu’administrateur du groupe, *john-doe@numerique.gouv.fr* peut effectuer diverses manipulations : ajouter, supprimer, ou changer le rôle d’un utilisateur.

Tous les utilisateurs du groupe de John héritent du scope `ecriture` sur ma-startup-d-etat.fr.

## Définitions


**Utilisateur** : un individu (agent public, prestataire, citoyen), identifié par son email

**Groupe** : un ensemble d’utilisateurs, appartenant a une organisation

**Organisation** : une structure identifiée par son numéro SIRET (ex: DINUM, `13002526500013`)

**Rôle** : le rôle d’un utilisateur au sein d'un groupe. (ex: `administrateur` ou `utilisateur`)

**Fournisseur de service** : un produit numérique (ex: une startup d’état)

**Scope** : la description des droits d’accès dont dispose un groupe, sur un fournisseur de service (ex: `ecriture` ou `lecture`)


## Utilisation

Afin de pouvoir utiliser cette API, il faut d’abord créer un compte de service pour votre fournisseur de service.

Ce compte de service vous permettra de vous authentifier sur l’API (OAuth2, voir la route /auth/token), et d’effectuer des opérations sur les utilisateurs, groupes, et rôles.

"""

api_tags_metadata = [
    {
        "name": "Authentification",
        "description": "Authentification (OAuth2)",
    },
    {
        "name": "Health check",
        "description": "Ping de l’application",
    },
    {
        "name": "Fournisseur de services",
        "description": "Votre fournisseur de service (ex: ma-startup-d-etat.fr)",
    },
    {
        "name": "Utilisateurs",
        "description": "Création et récupération des utilisateurs (les utilisateurs sont indépendants du fournisseur de service)",
    },
    {
        "name": "Rôles",
        "description": "Les rôles disponibles pour les utilisateurs (les utilisateurs sont indépendants du fournisseur de service)",
    },
    {
        "name": "Équipes",
        "description": "Création, et récupération des équipes",
    },
    {
        "name": "Administration d’une équipe",
        "description": "Doit nécessairement être executé par un administrateur de l’équipe",
    },
    {
        "name": "Gestion des droits d’une équipe",
        "description": "Permet de gérer les droits d’accès d’une équipe sur un fournisseur de service",
    },
]
