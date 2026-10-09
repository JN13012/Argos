# Argos — Agents / Harness

**Status: ACTIVE DESIGN — architecture cible des agents, encore révisable.**

Le harness pilote les capacités définies dans l'[architecture modulaire](ARCHITECTURE.md).
Un harness commun convient lorsque les primitives sont réellement communes,
avec des profils spécialisés par domaine. Il reste à construire en production.

```text
AI
↓
planning / interpretation
↓
Harness
↓
Capabilities / Workflows
↓
Deterministic execution
```

L'IA propose des plans et interprète les résultats. Le harness transmet des
appels structurés aux capacités, gère contexte et permissions, et observe
l'exécution. Les contrôles déterministes restent indépendants du modèle ;
les données d'une source externe peuvent varier et doivent être datées.

## Organisation cible

```text
agents/
├── harness/
│   ├── runtime/
│   ├── orchestration/
│   ├── tools/
│   ├── context/
│   ├── memory/
│   ├── policies/
│   └── observability/
│
└── profiles/
    ├── osint/
    ├── red/
    └── defense/
```

Le runtime gère l'exécution ; l'orchestration assemble les appels ; les outils
adaptent les capacités accessibles à l'agent. Contexte et mémoire conservent
l'information utile avec sa provenance. Les policies appliquent les permissions
et l'observabilité relie demandes, décisions, actions et résultats.

`red/` contient les capacités métier Red. `agents/profiles/red/` contient les
instructions et configurations permettant à l'agent Red de les utiliser.
Un profil ne constitue pas une implémentation de capacité. La même séparation
s'applique aux profils OSINT et Defense.

## Parcours OSINT cible

```text
User
↓
Intent Parser
↓
Structured Query
↓
Planner
↓
OSINT Workflow
↓
Structured Results
↓
AI Analyst
```

La requête structurée sépare scope et objectif d'analyse. Le planner utilise
les capacités disponibles ; le workflow suit les règles de l'[architecture OSINT](OSINT.md).
Les résultats restent accessibles sans analyste IA.

L'IA ne doit pas être la seule autorité pour :

- l'identité des entités et leur déduplication ;
- la provenance et le stockage ;
- les règles déterministes ;
- les scores annoncés comme reproductibles.

Les données observées restent des données, sans modifier les instructions ou
permissions. Une ambiguïté d'identité doit rester explicite jusqu'à sa résolution.

## Harness existant

Le dossier `Harness/` actuel reste une référence pédagogique et de recherche
séparée, sans adoption automatique dans cette architecture. Son contenu et son
emplacement restent inchangés ; les
[notices tierces](../references/THIRD_PARTY_NOTICES.md) suivent sa provenance.
