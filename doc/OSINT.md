# Argos OSINT — Principes du futur moteur

Ce document décrit une direction de conception, sans implémentation actuelle
ni schéma de données figé. La première verticale sera Business Discovery :
[trouver les garages de Marseille](SCOPE.md).

## Pipeline

```text
User Query
↓
Scope
↓
Discovery
↓
Entity Resolution
↓
Persistence
↓
Enrichment
↓
Analysis
↓
Ranking / Filtering
↓
Results
```

**Collect first, qualify later.** Le scope définit les entités à découvrir ;
l'objectif d'analyse définit ensuite leur interprétation. Une opportunité
commerciale supposée ne doit pas filtrer les résultats avant persistance.

## Concepts minimum

| Concept | Sens prévu |
| --- | --- |
| Entity | Objet réel stable, indépendant d'une recherche : d'abord organisation et établissement |
| Identifier | Identifiant permettant la résolution : SIRET, SIREN, domaine vérifié ou identifiant de provider |
| Observation | Fait collecté, accompagné de sa provenance et de sa date |
| Search | Recherche utilisateur avec scope, sources interrogées et résultats référencés |
| Coverage | Trace de la couverture obtenue et des limites rencontrées |

Website, Domain, Person ou Job pourront devenir d'autres types d'entités selon
des besoins futurs. Ils ne sont pas à implémenter dans la première tranche.
Des relations entre entités seront probablement nécessaires, par exemple entre
un établissement et une organisation ; elles n'imposent pas une base de graphes.

Une observation pourra conceptuellement porter :

```text
entity
field
value
source
observed_at
confidence
```

Les valeurs contradictoires et leurs sources devront rester visibles. Une valeur
retenue ou normalisée ne devra pas effacer silencieusement les faits collectés.

La couverture devra indiquer les sources interrogées, la pagination épuisée ou
non, les troncatures, les erreurs et les exclusions appliquées.
**Source exhausted ≠ all real-world entities found.** Une source épuisée ne
garantit pas que toutes les entités réelles du territoire ont été trouvées.

## Discovery

**« What entities exist in the requested scope? »**

Le moteur recherchera la meilleure couverture possible avec les sources
utilisées. Les entités découvertes dans le scope seront conservées avant
analyse, avec les limites de chaque recherche.

## Entity Resolution

Les premiers identifiants forts envisagés pour Business Discovery France sont :

- **SIRET** : identifie un établissement.
- **SIREN** : identifie une unité légale.

Deux établissements ayant le même SIREN resteront distincts. Un domaine partagé
ne suffira pas non plus à les fusionner. Une fusion ambiguë devra rester explicite,
avec ses candidats et les observations permettant une résolution ultérieure.

## Persistence

```text
New entity   → create
Known entity → reuse / update observations
```

Chaque entité aura un identifiant interne stable. Une recherche référencera
des entités persistantes au lieu de recréer un snapshot isolé de toutes les
données à chaque exécution. Les observations seront ajoutées ou actualisées en
conservant leur provenance. **SQLite est le backend initial envisagé.**

La persistance précédera l'enrichissement : toutes les entités découvertes
pourront être enregistrées sans exiger leur enrichissement complet immédiat.
Les données runtime locales resteront sous `.argos/`.

## Enrichment

**« What else can we learn about a known entity? »**

```text
Business → Website Resolution → Website Enrichment
```

La résolution devra justifier l'association d'une entité à son site officiel.
Une association incertaine ou un site inaccessible restera signalé ; l'absence
de site identifié ne prouve pas qu'aucun site existe.
L'enrichissement pourra être budgété ou priorisé et réutiliser les observations
encore pertinentes. Il ne conditionnera pas la conservation des entités.

## Analysis et classement

**« What do these observations mean for an objective? »**

Le premier cas prévu sera Website Opportunity Analysis. Les résultats dérivés
resteront séparés des observations sources. Un score devra être explicable,
recalculable et relié aux observations utilisées, avec ses limites.
Ranking / Filtering produira une vue sans supprimer les entités persistées.

## Sources / connectors

Un connector adaptera une source externe et devra prendre en compte pagination,
quotas, erreurs, provenance, conditions de stockage et couverture.
Le premier connecteur prévu concernera **SIRENE / Recherche d'Entreprises** ;
la source précise, ses conditions et ses limites seront validées avant intégration.
Aucun inventaire de providers n'est imposé.

## Frontière OSINT / Red

OSINT collectera et structurera des informations disponibles sans réaliser de
test offensif. Red testera activement une cible explicitement autorisée.

```text
OSINT → known assets → authorized Red workflow
```

Ce passage exigera une autorisation distincte. Les règles d'usage restent
définies dans le [cadre du projet](CADRE.md) ; aucune architecture Red n'est
développée ici.
