# Présentation de rôles.data

## Un nouveau schéma d’habilitation

```mermaid
flowchart TD
    U((Utilisateur))
    U-->D
    subgraph Dinum
        subgraph Datapass:        
            D[1. Nouvelle demande]-->|Validation|C[2. Habilitation]
            D-->|Refus|X[Demande refusée]
        end
        subgraph Roles.data:
            C-->|3. Création d’un groupe avec les droits associés| R[(Listes des groupes)]
        end
        subgraph ProConnect:
            L[Login]
        end
    end
    C-->|4. Envoi d’un mail a l'utilisateur l’invitaant a se connecter| U
    U-->|5. Clic sur le lien contenu dans le mail|A
    A<-->|6. Se ProConnecte|L
    subgraph Fournisseur de Service
        A[Accès au service]
        A<-->|7. Récupération des droits de l’utilisateur|R
    end
```

**Avantages :** 
- authentification, habilitation et délégation mutualisées et sécurisée
- charge technique réduite
- ouvre la possibilité du partage de groupe entre les produits
- parcours unifié, centré sur ProConnect

**Désavantages :**
- perte d’ownership et d'agilité pour le FS

