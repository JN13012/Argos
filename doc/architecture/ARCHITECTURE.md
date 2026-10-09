# Argos — Architecture modulaire

**Status: ACTIVE DESIGN — architecture cible, encore révisable avant implémentation.**

Cette organisation traduit la [vision](../product/VISION.md). Elle décrit la
cible, **pas l'arborescence actuelle ni une migration déjà réalisée**.

```text
argos/
├── core/
├── osint/
├── red/
├── defense/
└── agents/

frontend/
```

## Responsabilités

| Composant cible | Responsabilité |
| --- | --- |
| `core/` | Fonctions réellement transverses, partagées lorsque plusieurs domaines en ont besoin ; aucune logique métier propre à OSINT ou Red |
| `osint/` | Moteur de découverte, résolution, enrichissement et analyse ; référence : [OSINT](OSINT.md) |
| `red/` | Capacités métier offensives autorisées ; intégration ultérieure |
| `defense/` | Capacités défensives futures |
| `agents/` | Infrastructure d'agents et configurations spécialisées ; référence : [Agents / Harness](AGENTS_HARNESS.md) |
| `frontend/` | Interface utilisateur / UX commune aux modules, indépendante de la logique métier |

`argos/` rassemble la logique métier, les capacités, les agents et les contrats
internes. L'Interface reste un domaine fonctionnel de la vision produit, porté
par `frontend/`, sans imposer un package Python sous `argos/`. Une future API ou
couche d'adaptation pourra être ajoutée si un besoin concret le justifie ; aucun
package `argos/interface/` ou `argos/api/` n'est prévu à ce stade.

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

## Données runtime par domaine — cible

```text
.argos/
├── osint/
│   ├── db/
│   ├── raw/
│   ├── exports/
│   └── cache/
│
├── red/
│   ├── engagements/
│   ├── evidence/
│   ├── reports/
│   └── cache/
│
├── defense/
│   └── ...
│
└── shared/
    └── ...
```

Cette séparation évite de mélanger données OSINT, missions et preuves Red,
données Defense, exports et caches. `shared/` est réservé aux données réellement
communes. Les responsabilités du stockage et des sorties OSINT sont définies
dans [OSINT](OSINT.md#stockage-local-first).

**Cette structure est une cible documentaire ; ces dossiers ne sont pas
annoncés comme existants.** La structure physique exacte pourra évoluer.
Discovery V0 utilise toujours `.argos/discovery.sqlite3` par défaut ; les chemins
du Core et les exemples actuels restent inchangés. Aucun fichier runtime n'est
déplacé pendant cette passe.

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
