# Argos — Architecture minimale

## Architecture actuelle

Le dépôt contient la documentation de direction et une fondation Python minimale :
un package importable, une entrée CLI et un test d'import. Aucun module métier ni
workflow de CI n'est actif.

La fondation est construite sous :

```text
argos/
├── __init__.py
├── __main__.py
└── osint/
    └── __init__.py
```

Cette fondation ne définit aucun contrat de données ni implémentation métier.

## Direction future

Les domaines Red, Defense et Agents, ainsi qu'une interface utilisateur,
n'auront leurs dossiers que lorsqu'ils seront réellement développés.
Une API ou un noyau partagé nécessitera également un besoin démontré.
L'Interface représente l'UX du produit et n'impose pas un package Python.

## Capacités et orchestration

```text
Capability = ce qu'Argos sait faire
Workflow   = assemblage de capacités
Harness    = pilotage/orchestration par un agent
```

Les capacités métier devront rester utilisables sans agent. Un workflow les
assemblera ; un futur harness pourra piloter leur exécution et appliquer ses
permissions. L'interface présentera les recherches et leurs résultats.

L'[architecture OSINT](OSINT.md) porte les principes du premier moteur.
Le code futur vivra sous `argos/` ; `.argos/`, ignoré par Git, accueillera les
données runtime locales. Aucun arbre de stockage n'est créé maintenant.
