# Préparation GitHub et progression d'Argos

**Status: ARCHIVED / SUPERSEDED.**

Remplacée par la [roadmap OSINT prioritaire](../../project/ROADMAP.md).

Le contenu ci-dessous est conservé pour mémoire. Ses anciens statuts, décisions
et prochaines étapes ne définissent plus le corpus actif.

**Date initiale :** 7 octobre 2026. **État actualisé :** 9 octobre 2026.
**Statut :** Argos Core hors ligne implémenté, prototypes front et Discovery
réalisés séparément ; persistance/reprise Core proposée.

Cette feuille de route organise les réalisations et la progression proposée du
dépôt. Elle ne valide pas `01_SCOPE_V0_ARGOS.md` et ne remplace pas la vision
canonique. Le premier livrable a été accepté dans la conversation ; sa portée est
fixée dans [FIRST_DELIVERABLE.md](../deliverables/FIRST_DELIVERABLE.md). Il ne modifie pas les
engagements produit du scope V0 complet.

Pour une candidature, privilégier une petite réalisation vérifiable, une
attribution claire et des résultats mesurés. La vision produit reste disponible
comme perspective à long terme.

| Jalon | Livrable | Critère de terminé |
| --- | --- | --- |
| 1 — Préparer le dépôt | Nettoyage, `.gitignore` et documentation réalisés et publiés ; provenance des imports et traitement de l'historique à trancher | Aucun fichier de mission privée dans l'arbre courant ; origine des imports clarifiée ; décision explicite sur l'historique et la licence |
| 2 — Première démo hors ligne | Implémenté : création, import, validation, revue humaine et rapport synthétique | Une commande documentée produit le même rapport depuis un clone propre, sans service externe ni cible réseau |
| 3 — Qualité du noyau | Implémenté : modules de données, validation et rapport ; erreurs utiles ; tests et CI | Tests de données invalides, preuves manquantes et export ; CI verte ; installation reproductible |
| 4 — Évaluation documentée | Jeu synthétique et cas négatifs présents ; campagnes, métriques et comparaison de versions à définir | Résultats reproductibles sur la qualité des rapports, les erreurs de validation, le temps et le coût ; limites publiées |
| 5 — Présentation portfolio | À compléter : démo courte, captures, schéma d'architecture et première release | Un recruteur comprend l'objectif, la contribution personnelle et les résultats en quelques minutes |

## Première tranche implémentée

Argos Core 0.1.0 fournit une CLI Python sans dépendances d'exécution : création de
mission, import de constats, validation des preuves, revue humaine et export
Markdown. Les données sont synthétiques et la démo est indépendante des imports
pédagogiques. Python est fixé pour ce lot, sans figer la stack du produit final.

Le schéma, les cas d'acceptation et les commandes sont documentés dans la fiche
du livrable. Des tests et une CI couvrent la chaîne hors ligne. La prochaine
tranche proposée porte sur la persistance et la reprise de missions, avec un
contrat à définir avant implémentation.

## Prototypes et documentation déjà réalisés

- **Front React/TypeScript :** accueil interactif réalisé, avec dossier
  synthétique, rapport correspondant, recherche, journal de session et chat
  local. Il reste un prototype séparé, sans connexion à Argos Core, Discovery
  ou un modèle IA. Voir le [guide du front](../../interface/FRONTEND.md).
- **Discovery V0 :** prototype indépendant de découverte d'entreprises,
  qualification et snapshots SQLite/JSON. Sa
  [fiche de périmètre](../../livrables/DISCOVERY_V0.md) conserve explicitement la
  contradiction entre l'enrichissement commercial et l'OSINT technique du
  draft V0 ; aucun rattachement officiel au scope produit n'est décidé ici.
- **Documentation :** regroupement sous `doc/` et sommaire réalisés le
  9 octobre. Le [statut du projet](PROJECT_STATUS_ARGOS.md) suit les réalisations,
  et le [manifeste](CANONICAL_MANIFEST_ARGOS.md) leurs statuts documentaires.

Ces réalisations ne terminent pas les cinq incréments de la plateforme V0.
La persistance de snapshots Discovery ne constitue pas la reprise de missions
Argos Core proposée pour le prochain lot.

## Inspirations et limites des comparaisons

[XBOW](https://docs.xbow.com/console/get-started/introduction/),
[Strix](https://github.com/usestrix/strix) et
[NoScope](https://www.noscope.com/) sont des références citées pour la vision
d'outils de sécurité assistés par IA. Ce dépôt ne les a pas évalués et ne revendique
aucune équivalence. Les fonctions annoncées par les éditeurs ne sont pas des
résultats mesurés pour Argos.

Les prochaines décisions d'architecture peuvent porter sur la traçabilité,
l'analyse statique en lecture seule, la revue humaine, la protection des données
et l'évaluation hors ligne. Les capacités réseau/Linux et Windows/AD du brief
restent des sujets du scope proposé, sans implémentation ni promesse de délai
dans cette feuille de route de présentation.

Une [revue des projets voisins](../../references/RELATED_PROJECTS.md) précise les références à
étudier, les licences annoncées et les éléments de conception utiles aux prochains
lots. Le course pack a été retiré du dossier courant ; les références
pédagogiques conservées demandent encore une attribution vérifiée.
