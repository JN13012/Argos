# Documentation Argos

Ce dossier rassemble la documentation du projet. Les documents sont classés
par usage ; leurs statuts restent précisés dans le manifeste et dans chaque
fiche. Le déplacement des fichiers ne valide pas le scope V0 proposé.

Pour démarrer, lire le [guide de démarrage](guides/DEMARRAGE.md). Pour développer
le noyau hors ligne, lire le [contrat du premier livrable](livrables/FIRST_DELIVERABLE.md)
et les [instructions du dépôt](../AGENTS.md). Pour tester l'accueil Web, suivre
le [guide du front](interface/FRONTEND.md).

## Classement

| Dossier | Type de documentation |
| --- | --- |
| `produit/` | Vision, positionnement et proposition de scope |
| `suivi/` | Autorité des documents, statut, feuille de route et revues du dépôt |
| `livrables/` | Périmètres, contrats et critères d'acceptation des lots réalisés |
| `guides/` | Démarrage, démonstrations, utilisation et vérifications |
| `interface/` | Développement du front, choix de présentation et ressources visuelles |
| `references/` | Projets voisins, provenance et attribution des imports |

## Produit

| Document | Contenu | Statut |
| --- | --- | --- |
| [Product Brief et plan global](produit/00_PRODUCT_BRIEF_ET_PLAN_GLOBAL_ARGOS.md) | Vision et décisions fondatrices | Vision approuvée, version 2.5 |
| [Scope V0](produit/01_SCOPE_V0_ARGOS.md) | Proposition de périmètre et d'acceptation de la plateforme | `IN_PROGRESS`, version 1.0 |

## Suivi du projet

| Document | Contenu |
| --- | --- |
| [Manifeste canonique](suivi/CANONICAL_MANIFEST_ARGOS.md) | Versions, statuts, dépendances et ordre d'autorité |
| [Statut du projet](suivi/PROJECT_STATUS_ARGOS.md) | Travail terminé, décisions actives et prochaines étapes |
| [Feuille de route](suivi/ROADMAP.md) | Progression proposée pour la démo et le portfolio |
| [Revue du dépôt](suivi/REPOSITORY_REVIEW.md) | Préparation à la publication et constats historiques datés |

## Livrables

| Document | Contenu |
| --- | --- |
| [Premier livrable : Argos Core hors ligne](livrables/FIRST_DELIVERABLE.md) | Contrat des missions, import, preuves, revue humaine et rapports |
| [Prototype Discovery V0](livrables/DISCOVERY_V0.md) | Découverte d'entreprises, sources, scores et snapshots ; lot indépendant du scope V0 de la plateforme |

## Guides

| Document | Contenu |
| --- | --- |
| [Démarrage et vérifications](guides/DEMARRAGE.md) | Installation, démos, parcours de mission, structure du dépôt et contrôles |
| [Exemple hors ligne](guides/EXEMPLE_HORS_LIGNE.md) | Données synthétiques, preuves et rapport de référence |
| [Exemples Discovery](guides/EXEMPLES_DISCOVERY.md) | Entreprises fictives et réponses Web simulées |

## Interface

| Document | Contenu |
| --- | --- |
| [Guide du front](interface/FRONTEND.md) | Lancement, interactions, architecture, données et tests |
| [Revue de l'accueil](interface/HOME_DESIGN_REVIEW.md) | Présentation restaurée, cohérence des données et limites du chat |
| [Ressources visuelles](interface/RESSOURCES_VISUELLES.md) | Origine et utilisation des mascottes et des icônes |

## Références

| Document | Contenu |
| --- | --- |
| [Projets voisins](references/RELATED_PROJECTS.md) | Sources d'inspiration et observations de licences, datées de la revue |
| [Origine des éléments importés](references/THIRD_PARTY_NOTICES.md) | Provenance et attribution des supports tiers |

## Conventions

Les liens entre documents sont relatifs au fichier consulté. Les chemins de code
et les commandes sont relatifs à la racine du dépôt, sauf indication explicite
dans le guide du front. Les noms des documents produit restent stables ; les
documents seulement planifiés dans le manifeste n'ont pas de fichier créé.

Le [README de la racine](../README.md) sert d'entrée et `AGENTS.md` conserve les
instructions opérationnelles attendues par les outils. Les schémas restent dans
`schemas/`, les fixtures et rapports de référence dans `examples/` et
`frontend/assets/`. Les supports importés sous `Harness/` conservent leur
organisation et leur provenance séparées.
