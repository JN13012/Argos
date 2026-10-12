# Argos — Vision

Argos vise une plateforme modulaire pour collecter, structurer et analyser des
informations utiles à l'OSINT et à la cybersécurité. **Current priority = OSINT.**

```text
Argos
├── OSINT
├── Red
├── Defense
├── Agents / Harness
└── Interface
```

OSINT constitue le domaine actif de conception. Red, Defense, Agents / Harness
et Interface sont des directions futures, sans implémentation actuelle.

## Principes

- **Modularité** : introduire chaque capacité pour un besoin concret.
- **AI-assisted, not AI-dependent** : l'IA pourra aider à interpréter et
  analyser ; les capacités essentielles devront fonctionner sans modèle.
- **Provenance** : conserver la source, la date et les limites des observations.
- **Local-first lorsque pertinent** : privilégier l'exécution et les données
  locales sans imposer d'infrastructure distante.
- **Séparation** : distinguer capacités métier, orchestration et interface.
- **Extensibilité** : faire évoluer sources et analyses indépendamment, par
  étapes validées.

Le dépôt contient actuellement de la documentation, sans application active.
Le [scope](SCOPE.md) fixe le prochain travail ; le [cadre](CADRE.md) définit
l'usage prévu et l'[architecture](ARCHITECTURE.md) la direction minimale.
