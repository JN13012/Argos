# Argos — Architecture modulaire

**Status: ACTIVE / CANONICAL — architecture cible.**

Cette organisation traduit la [vision](../product/VISION.md). Elle décrit la
cible, **pas l'arborescence actuelle ni une migration déjà réalisée**.

```text
argos/
├── osint/
├── red/
├── defense/
├── agents/
│   ├── harness/
│   └── profiles/
├── core/
└── interface/
```

## Responsabilités

| Module cible | Responsabilité |
| --- | --- |
| `core/` | Fonctions réellement transverses, partagées lorsque plusieurs domaines en ont besoin ; aucune logique métier propre à OSINT ou Red |
| `osint/` | Moteur de découverte, résolution, enrichissement et analyse ; référence : [OSINT](OSINT.md) |
| `red/` | Capacités métier offensives autorisées ; intégration ultérieure |
| `defense/` | Capacités défensives futures |
| `agents/` | Infrastructure d'agents et configurations spécialisées ; référence : [Agents / Harness](AGENTS_HARNESS.md) |
| `interface/` | Adaptateurs et contrats d'accès aux capacités ; présentation indépendante de la logique métier |

Le partage dans `core/` doit répondre à un besoin démontré. Le nom actuel
« Argos Core » désigne le livrable hors ligne ; il ne signifie pas qu'un dossier
`argos/core/` existe déjà.

## Capacités, pilotage et assemblage

```text
Capability = ce qu'Argos sait faire
Harness = comment un agent pilote les capacités
Workflow = comment plusieurs capacités sont assemblées
```

Les capacités restent appelables sans agent. Un workflow assemble des capacités
avec des entrées et sorties structurées. Le harness pilote cette exécution et
applique ses permissions ; l'interface présente les résultats.

```text
agents/
├── harness/
└── profiles/
    ├── osint/
    ├── red/
    └── defense/
```

## État du dépôt

Le code Discovery reste sous `argos/discovery/`, les modules de la CLI hors ligne
directement sous `argos/` et le frontend React sous `frontend/`. L'arborescence
cible ne prescrit pas de déplacer le frontend dans le paquet Python.
Le [statut](../project/STATUS.md) tient l'inventaire de l'implémentation.

Le dossier actuel `Harness/` est un artefact pédagogique et de recherche, avec
une provenance à clarifier. Il n'est pas automatiquement le futur harness de
production. Il reste séparé et n'est ni déplacé ni restructuré dans cette étape
documentaire. Sa provenance est suivie dans les
[notices tierces](../references/THIRD_PARTY_NOTICES.md).
