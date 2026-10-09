# Argos OSINT — Architecture

**Status: ACTIVE DESIGN — référence principale de l'architecture OSINT cible, encore révisable.**

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

`argos/osint/storage/` désigne le **code de persistance** : repositories,
interfaces et adapters de stockage. `.argos/osint/` désigne les **données runtime
locales**, réparties dans `db/`, `raw/`, `exports/` et `cache/`. Cette distinction
entre code et données décrit la cible ; les chemins actuels restent inchangés.

## Frontière OSINT Cyber / Red

Les familles `connectors/cyber/`, `discovery/cyber_assets/`, `enrichment/cyber/`
et `analysis/cyber_surface/` construisent une connaissance de surface à partir
d'informations disponibles. OSINT Cyber reste principalement passif, public et
non intrusif ; l'accès à une source restreinte doit être explicitement autorisé.

Exemples de sources et d'observations OSINT :

- Domaines, WHOIS / RDAP, DNS public, Certificate Transparency et certificats publics.
- ASN, données publiques sur les IP, technologies observables et métadonnées publiques.
- Repositories publics et sources de threat intelligence autorisées.
- Historique de domaines ou du Web lorsque légalement disponible.

`red/` commence avec l'interaction active visant à tester la sécurité d'une
cible explicitement autorisée :

- Port scanning et service enumeration actifs.
- Directory/content discovery actif et crawling offensif approfondi.
- Fuzzing, vulnerability scanning et authentication testing.
- Exploitation, post-exploitation et validation active de vulnérabilités.

La frontière tient à la finalité et aux techniques : une lecture ordinaire d'une
source publique ou d'un site déclaré pour l'enrichissement OSINT n'est pas un
test actif de sécurité. L'autorisation de consulter une source n'autorise pas
automatiquement à tester les actifs qu'elle mentionne.

```text
OSINT answers:
"What can we learn about the target from available information?"

Red answers:
"What can we actively test on an explicitly authorized target?"
```

Un workflow Red pourra consommer les données OSINT dans son propre scope autorisé :

```text
OSINT
↓
known domains / assets / context
↓
authorized Red workflow
↓
active validation
```

Ces exemples fixent une frontière de design ; aucune capacité n'est déplacée
dans le code pendant cette étape.

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

Dans la première phase cible, **SQLite est la source structurée principale**.
La connaissance interne ne doit pas être dispersée dans des fichiers JSON
indépendants. La séparation des responsabilités est la suivante :

```text
Structured knowledge  → database
Raw artifacts         → files/object storage
Large analytical data → Parquet when useful
Exports               → JSON / CSV / Parquet
```

La [structure runtime par domaine](ARCHITECTURE.md#données-runtime-par-domaine--cible)
sépare OSINT des missions et preuves Red, des données Defense et des données
partagées. Organisation OSINT cible :

```text
.argos/osint/
├── db/
│   └── argos-osint.sqlite3
├── raw/
├── exports/
└── cache/
```

| Élément | Responsabilité cible |
| --- | --- |
| `db/` | Données structurées persistantes : entités, observations, provenance, analyses et relations pertinentes |
| `raw/` | Réponses API brutes utiles, HTML, documents et snapshots nécessaires à la preuve ou au retraitement |
| `exports/` | Sorties générées pour l'utilisateur ou un consommateur externe : JSON, CSV, Parquet ou autres formats selon le besoin |
| `cache/` | Données temporaires supprimables, jamais considérées comme source persistante de vérité |

**Cette structure est une cible documentaire ; elle ne décrit pas des dossiers
déjà créés.** La structure physique exacte pourra évoluer. Le runtime reste sous
le répertoire ignoré `.argos/`. **`.argos/discovery.sqlite3` reste la base par
défaut de Discovery V0** tant que le code n'est pas migré. Les nouveaux formats
d'export et le stockage des pages brutes ne sont pas annoncés comme implémentés.

### Storage et outputs

Le storage porte la connaissance persistante interne, dans `.argos/osint/db/`
et les artefacts utiles de `.argos/osint/raw/`. Les outputs sont des résultats
générés pour consommation externe ou utilisateur.

Le choix cible est **`.argos/osint/exports/`** : la séparation des responsabilités
au sein du domaine suffit. Un dossier `.argos/outputs/<domaine>/` faciliterait
le regroupement transversal des sorties, mais ajouterait une seconde
arborescence par domaine sans besoin établi aujourd'hui.

**Un export doit pouvoir être supprimé et régénéré à partir des données
conservées, sans supprimer la connaissance principale.** La régénération ne
doit pas dépendre d'un cache jetable. L'export n'est pas la source de vérité.

### Données brutes et conservation

Conserver un maximum de connaissance utile sans perte silencieuse d'information
pertinente ne signifie pas conserver chaque octet collecté pour toujours.

- **Observation normalisée** : conservation durable selon la politique de rétention,
  avec sa provenance ; un retrait ou un conflit ne doit pas effacer silencieusement
  une information pertinente.
- **Raw artifact** : conservation lorsqu'il apporte une valeur pour la provenance,
  la preuve, le retraitement, l'audit ou l'évolution d'un parser.
- **Cache** : jetable, séparé de la connaissance persistante.

Une déduplication de contenu pourra éviter plusieurs copies identiques d'un
artefact, par exemple avec `SHA-256(raw artifact)`, tout en conservant les
références de source et de collecte distinctes. Les durées de rétention et ce
mécanisme restent à définir avant implémentation.

### Évolutions possibles

Selon les besoins : `SQLite → PostgreSQL`, fichiers bruts locaux vers un stockage
`MinIO / S3 compatible`, grands jeux analytiques vers `Parquet`. Ces évolutions
ne sont pas des migrations immédiates. La logique métier dépend de contrats de
stockage, pas du backend ; aucun service cloud ni nouvelle dépendance n'est
requis par cette étape documentaire.

## Écart avec l'implémentation actuelle

Discovery reste sous `argos/discovery/`. Il enrichit et score avant de sauvegarder
un snapshot de recherche ; la persistance avant enrichissement, l'upsert global
d'entités et le rafraîchissement partagé restent à construire. Ses bornes de
sources et de résultats limitent aujourd'hui les entités conservées. Le
[contrat Discovery V0](../livrables/DISCOVERY_V0.md) décrit ces comportements ;
le [statut](../project/STATUS.md) suit les écarts restants.
