# Argos — Vision

**Status: CANONICAL — vision produit validée.**

Argos vise une plateforme modulaire pilotée par IA pour collecter, structurer,
analyser et exploiter des informations utiles à la cybersécurité, à l'OSINT et
à l'automatisation. **La priorité actuelle est Argos OSINT.**

```text
Argos
├── OSINT
├── Red
├── Defense
├── Agents / Harness
└── Interface
```

## Modules

- **OSINT** : discovery, collecte, résolution d'identité des entités
  (*entity resolution*), enrichissement et analyse.
- **Red** : capacités offensives autorisées Web/API, réseau, systèmes et Active
  Directory ; exploitation, validation, preuves et reporting. Module futur.
- **Defense** : capacités défensives futures, à cadrer selon les besoins.
- **Agents / Harness** : infrastructure commune de contexte, outils, policies,
  mémoire, workflows, permissions et observabilité.
- **Interface** : interface commune aux modules, indépendante de la logique
  métier.

## Principes

- **Modularité** : chaque domaine possède ses capacités et ses responsabilités.
- **AI-assisted, not AI-dependent** : l'IA aide à interpréter, planifier et
  analyser ; les capacités essentielles restent utilisables sans modèle.
- **Local-first** : données et exécution locales en première intention.
- **Provenance** : chaque information exploitable garde son origine et sa date.
- **Extensibilité** : sources, capacités et analyses peuvent évoluer séparément.
- **Séparation** : logique métier, orchestration et interface restent distinctes.

Cette vision décrit la direction du produit. Red, Defense et l'infrastructure
d'agents de production restent à construire ; les prototypes existants ne
démontrent pas la plateforme complète. Le [scope actif](SCOPE.md) fixe le travail
prioritaire, l'[architecture](../architecture/ARCHITECTURE.md) décrit la cible et
le [statut](../project/STATUS.md) décrit ce qui existe.
