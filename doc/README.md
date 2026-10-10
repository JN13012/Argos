# Documentation Argos

Argos vise une plateforme modulaire : OSINT, Red, Defense, Agents / Harness et
Interface. **La priorité actuelle est OSINT.** Le corpus actif distingue la
direction produit, l'architecture cible et les prototypes réellement existants.

## Start here

| Ordre | Document | Statut | Question traitée |
| --- | --- | --- | --- |
| 1 | [VISION](product/VISION.md) | `CANONICAL` | Que vise Argos ? |
| 2 | [SCOPE](product/SCOPE.md) | `CANONICAL` | Quel est le périmètre actif ? |
| 3 | [CADRE](product/CADRE.md) | `CANONICAL` | Dans quel cadre académique et éthique Argos est-il développé ? |
| 4 | [ARCHITECTURE](architecture/ARCHITECTURE.md) | `ACTIVE DESIGN` | Comment les modules cibles se séparent-ils ? |
| 5 | [OSINT](architecture/OSINT.md) | `ACTIVE DESIGN` | Comment découvrir, conserver, enrichir et analyser les entités ? |
| 6 | [STATUS](project/STATUS.md) | `ACTIVE` | Qu'est-ce qui existe aujourd'hui ? |
| 7 | [ROADMAP](project/ROADMAP.md) | `ACTIVE` | Dans quel ordre progresser ? |

Le document [AGENTS_HARNESS](architecture/AGENTS_HARNESS.md), `ACTIVE DESIGN`,
précise le pilotage des capacités. Le [manifeste](project/CANONICAL_MANIFEST.md)
distingue les décisions produit `CANONICAL`, le design révisable `ACTIVE DESIGN`,
le suivi `ACTIVE`, puis les notes d'implémentation, références et archives.

## Implementation notes

- [Discovery V0](livrables/DISCOVERY_V0.md) : contrat et historique de la première
  implémentation OSINT Discovery, toujours sous `argos/discovery/`.
- [Premier livrable Core](livrables/FIRST_DELIVERABLE.md) : page de compatibilité
  vers le contrat archivé du lot hors ligne livré, dont le comportement est
  inchangé. Ce contrat ne définit pas la nouvelle direction produit.
- [AGENTS.md](../AGENTS.md) : instructions opérationnelles du dépôt, conservées
  pour le lot hors ligne.

## Frontend

- [FRONTEND](interface/FRONTEND.md) : accueil React, lancement, données et tests.
- [Ressources visuelles](interface/RESSOURCES_VISUELLES.md) : origine et usage des
  images et icônes.

Le frontend reste dans `frontend/`, sans connexion aux moteurs ni modèle IA.

## Guides

- [Démarrage et vérifications](guides/DEMARRAGE.md).
- [Exemple hors ligne](guides/EXEMPLE_HORS_LIGNE.md).
- [Exemples Discovery](guides/EXEMPLES_DISCOVERY.md).

## References

- [RELATED_PROJECTS](references/RELATED_PROJECTS.md) : recherche et observations
  datées sur des projets voisins, sans autorité produit ou architecturale.
- [THIRD_PARTY_NOTICES](references/THIRD_PARTY_NOTICES.md) : provenance des imports,
  conservée sans modification.

## Archive

L'[index des archives](archive/README.md) donne accès à l'ancien Product Brief,
au scope V0 offensif, à l'ancien suivi, au premier livrable et aux revues
terminées. Ces documents ne font plus autorité sur la direction active.

## Conventions

Les liens Markdown sont relatifs au document. Les commandes et chemins de code
sont relatifs à la racine du dépôt, sauf indication explicite. Le
[README racine](../README.md) sert d'entrée courte.

L'organisation anglaise `product/`, `architecture/` et `project/` porte le
corpus actif ; `livrables/`, `guides/`, `interface/` et `references/` conservent les
notes utiles. Cette réorganisation est exclusivement documentaire : aucun code,
schéma, fixture ou import `Harness/` n'est déplacé. Les données générées restent
localement sous `.argos/`, ignoré par Git.
