# Argos — Architecture minimale

## Architecture actuelle

Le dépôt contient un package Python `argos`, un CLI OSINT avec découverte SIRENE,
persistance SQLite et rapports, ainsi qu'une API FastAPI minimale et son frontend.
Le Pentest Engine, les plans d'autorisation et d'exécution ne sont pas
implémentés.

La fondation est construite sous :

```text
argos/
├── __main__.py, cli.py
├── backend/
│   ├── api/                  FastAPI et routes HTTP
│   ├── core/                 Configuration et réponses d'erreur communes
│   ├── intel/osint/           Modèles, services et adaptateurs OSINT
│   └── attack/pentest/       Frontière réservée, sans implémentation active
└── frontend/                 React + TypeScript + Vite
```

Le CLI reste exposé via `argos.cli` et `python -m argos`. Les imports historiques
`argos.osint` redirigent vers le package canonique
`argos.backend.intel.osint`, sans dupliquer la logique métier.

Le `pyproject.toml` et `uv.lock` racine pilotent le package Python unique.
Le frontend conserve un `package.json` et un lock npm dans `argos/frontend/`.
Les documents de gouvernance restent classés sous `docs/product/` et ne sont
pas modifiés par cette organisation.

## Capacités et orchestration

```text
Capability = ce qu'Argos sait faire
Workflow   = assemblage de capacités
Harness    = pilotage/orchestration par un agent
```

Les capacités métier devront rester utilisables sans agent. Un workflow les
assemblera ; un futur harness pourra piloter leur exécution et appliquer ses
permissions. L'interface présentera les recherches et leurs résultats.

Les [principes OSINT](../product/OSINT.md) portent la conception du moteur.
`.argos/`, ignoré par Git, et `outputs/`, également ignoré, restent à la racine
pour les données runtime locales et les rapports. Aucun contenu local n'est
déplacé par la migration.
