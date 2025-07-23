# Présentation de rôles.data

## Pourquoi rôles.data

### Avant
```mermaid
flowchart TD
    U(Utilisateur)-->C
    subgraph FS:
        C[Page de connexion] -->|Verification| B
        B[Base utilisateur] --> A
        A[Accès au site]
    end
```

Avantages : 
- contrôle technique sur toute la chaine

Désavantages
- charge technique de toute la chaine
- pas de mutualisation des bases utilisateurs 
- gestion des habilitations/demandes d’accès minimaliste

### Aujourd'hui (outils opérateur)
```mermaid
flowchart TD
    U(Utilisateur)-->C
    subgraph ProConnect:        
        C[Page de connexion]
    end
    subgraph FS:
        C-->|Utilisateur vérifié| B
        B[Base utilisateur] --> A
        A[Accès au site]
    end
    subgraph "Datapass":        
        MCP[Connexion MoncomptePro] --> H[Formulaire habilitation]
        H-->|Nouveaux droits| B
    end
    U-->|Demande d’habilitation| MCP
```

Avantages : 
- authentification et habilitation mutualisée
- charge technique réduite

Désavantages
- perte d’ownership et d'agilité pour le FS
- lourdeur du parcours
  - MCP <> ProConnect
  - pas de délégation de droits (besoin de faire un datapass par user)

### Demain (avec rôles.data)

```mermaid
flowchart TD
    U(Utilisateur)-->C
    subgraph ProConnect:        
        C[Page de connexion]
    end
    subgraph FS:
        V[vérification des droits] -->|Si droits suffisants| A[Accès au site]
    end
    subgraph "Roles.data": 
        C-->|Utilisateur vérifié| V
        V<-->B[Groupes et des droits]
    end
    subgraph "Datapass":        
        C -->|Demande d’habilitation| H[Formulaire habilitation]
        H-->|Nouveaux droits| B
    end
```

Avantages : 
- authentification, habilitation et délégation mutualisées
- charge technique réduite
- ouvre la possibilité du partage de groupe entre les produits
- parcours unifié, centré sur ProConnect

Désavantages
- perte d’ownership et d'agilité pour le FS

NB: possibilité d'aller bien plus loin dans l'intégration ProConnecto, Datapasso et Rolo
