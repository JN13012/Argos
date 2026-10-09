# Argos OSINT — Architecture

**Status: ACTIVE / CANONICAL — référence principale de l'architecture OSINT cible.**

Le [scope actif](../product/SCOPE.md) donne la priorité à Business Discovery +
Website Opportunity. Les structures et exemples ci-dessous sont des objectifs
de conception, pas un nouveau schéma public ni des capacités déjà livrées.
[Discovery V0](../livrables/DISCOVERY_V0.md) documente le contrat actuel.

## Organisation cible

```text
argos/osint/
│
├── core/
│   ├── entities/
│   ├── observations/
│   ├── provenance/
│   ├── identity_resolution/
│   └── query/
│
├── connectors/
│   ├── registries/
│   ├── search/
│   ├── maps/
│   ├── websites/
│   ├── social/
│   ├── jobs/
│   └── cyber/
│
├── discovery/
│   ├── business/
│   ├── people/
│   ├── jobs/
│   ├── communities/
│   └── cyber_assets/
│
├── enrichment/
│   ├── business/
│   ├── website/
│   ├── professional/
│   ├── social/
│   └── cyber/
│
├── analysis/
│   ├── website_opportunity/
│   ├── ai_opportunity/
│   ├── mobile_opportunity/
│   ├── career_match/
│   ├── audience_relevance/
│   └── cyber_surface/
│
├── workflows/
└── storage/
```

**Tous ces dossiers ne doivent pas être implémentés immédiatement.** Seuls les
composants utiles à la première verticale sont à introduire progressivement.
Les connecteurs adaptent les sources ; discovery découvre des entités,
enrichment ajoute des observations, analysis produit des interprétations et
workflows assemble ces capacités. Le noyau OSINT porte les concepts propres à
ce domaine, distincts des fonctions transverses d'Argos.

## Pipeline

```text
User Query
↓
Intent / Scope
↓
Discovery
↓
Entity Resolution
↓
Database Upsert
↓
Enrichment
↓
Analysis
↓
Ranking / Filtering
↓
Results
```

L'intention distingue les critères du scope et l'objectif d'analyse. Une
opportunité recherchée ne devient pas un critère de rejet avant collecte.

## Discovery

Répond : **« Quelles entités correspondent au scope ? »** Le moteur recherche
la meilleure couverture possible à travers les sources disponibles, en rendant
visibles sources interrogées, limites et couverture incomplète. L'IA ne filtre
pas les entités selon leur intérêt supposé. Toutes les entités trouvées dans le
scope sont conservées avant l'analyse.

## Entity Resolution

La résolution distingue une entité nouvelle, une entité déjà connue, un doublon
et une identité ambiguë. Ordre de priorité des signaux :

1. SIRET.
2. SIREN.
3. Autres identifiants officiels.
4. Domaine officiel vérifié.
5. Adresse.
6. Téléphone.
7. Autres signaux.

La granularité compte : un SIRET identifie un établissement, un SIREN une unité
légale. Plusieurs établissements d'une même entreprise restent distincts.
Un domaine partagé ne suffit pas à les fusionner. Les signaux doivent être
cohérents et les identifiants contradictoires restent explicites.
**Aucune fusion ambiguë automatique** : conserver les candidats et les éléments
permettant une résolution ultérieure.

## Storage / Upsert

Chaque entité possède un identifiant Argos stable, indépendant d'une recherche.

```text
Nouvelle entité   → CREATE
Entité existante  → UPDATE / APPEND OBSERVATIONS
```

Une nouvelle recherche rattache ses résultats aux entités connues et ne recrée
pas de doublon. L'entité et ses premières observations sont persistées avant
enrichissement ; les étapes suivantes y ajoutent leurs résultats.

## Observations et provenance

Les faits collectés sont conservés individuellement. Exemple conceptuel
d'observation, sans imposer un format physique :

```text
entity
field
value
source
collected_at
confidence
```

Les anciennes observations peuvent être conservées, y compris lors d'un conflit
ou d'un rafraîchissement. Une valeur retenue ne doit pas effacer silencieusement
les faits qui ont permis de la choisir. Conserver la provenance lorsqu'approprié :

```text
source
source_url
provider
collected_at
raw_value
normalized_value
confidence
```

## Enrichment

Répond : **« Que pouvons-nous apprendre de plus sur cette entité ? »**

```text
Business
→ Website Resolver
→ Official Website
→ Website Enrichment
```

Le resolver cherche une association justifiée entre entité et site officiel,
puis l'enrichissement collecte des observations. Une association incertaine ou
un site inaccessible reste signalé. L'absence de site identifié ne prouve pas
l'absence de site.

## Analysis

Répond : **« Que signifient les données pour un objectif donné ? »** Une même
entité peut recevoir des analyses Website Opportunity, AI Automation
Opportunity, Mobile Opportunity, Career Relevance ou d'autres objectifs.
Ces familles sont des extensions possibles ; Website Opportunity est prioritaire.

Les analyses référencent les observations utilisées et ne modifient pas les
données sources. Les résultats dérivés restent distincts des faits collectés.

## Ranking / Filtering

Le classement intervient après collecte et enrichissement. Modifier un scoring
doit permettre de recalculer l'analyse sur les observations conservées sans
relancer une découverte complète. Version de l'analyse, données utilisées et
limites doivent permettre d'expliquer les scores annoncés comme reproductibles.

## Réutilisation et concurrence

```text
Existing entity
↓
Check freshness
↓
Reuse valid data
↓
Refresh stale/missing data
↓
Append observations
```

Les règles de fraîcheur restent à définir selon les sources et les champs.
L'ordre logique reste `Discovery → Resolution → Storage → Enrichment`.
Une fois les entités persistées, la découverte d'autres entités et
l'enrichissement des entités enregistrées peuvent s'exécuter concurremment.
Cette possibilité n'annonce pas une concurrence déjà implémentée.

## Stockage local-first

Organisation logique de la première phase, sans figer le chemin sur disque :

```text
local OSINT data/
├── argos-osint.sqlite3
├── raw/
├── exports/
└── cache/
```

| Élément | Responsabilité cible |
| --- | --- |
| SQLite | Base structurée de la première phase : entités, observations et résultats liés |
| `raw/` | Réponses ou documents bruts conservés lorsqu'ils apportent une valeur réelle |
| `exports/` | JSON, CSV ou Parquet selon le besoin ; ces formats ne sont pas tous disponibles aujourd'hui |
| `cache/` | Données temporaires supprimables, distinctes des observations persistantes |

Les données générées restent localement sous le répertoire ignoré `.argos/`
utilisé par le dépôt. Les noms ci-dessus décrivent des responsabilités ; ils
ne renomment pas la base actuelle `.argos/discovery.sqlite3`.

Évolutions possibles selon les besoins : `SQLite → PostgreSQL`, fichiers bruts
locaux vers `MinIO / S3`, grands jeux analytiques vers `Parquet`. La logique
métier dépend de contrats de stockage, pas du backend. Aucun service cloud ni
nouvelle dépendance n'est requis par cette étape documentaire.

## Écart avec l'implémentation actuelle

Discovery reste sous `argos/discovery/`. Il enrichit et score avant de sauvegarder
un snapshot de recherche ; la persistance avant enrichissement, l'upsert global
d'entités et le rafraîchissement partagé restent à construire. Ses bornes de
sources et de résultats limitent aujourd'hui les entités conservées. Le
[contrat Discovery V0](../livrables/DISCOVERY_V0.md) décrit ces comportements ;
le [statut](../project/STATUS.md) suit les écarts restants.
