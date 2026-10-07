# Préparation GitHub et progression d'Argos

**Date :** 7 octobre 2026. **Statut :** proposition de travail.

Cette feuille de route organise la présentation du dépôt et propose une première
démo. Elle ne valide pas `01_SCOPE_V0_ARGOS.md` et ne remplace pas la vision
canonique. Le périmètre du premier livrable doit être décidé avant de modifier
les engagements produit existants.

Pour une candidature, privilégier une petite réalisation vérifiable, une
attribution claire et des résultats mesurés. La vision produit reste disponible
comme perspective à long terme.

| Jalon | Livrable | Critère de terminé |
| --- | --- | --- |
| 1 — Préparer le dépôt | Nettoyage, `.gitignore`, README, revue, provenance des imports | Aucun fichier de mission dans la version publique ; origine des imports clarifiée ; décision explicite sur l'historique et la licence |
| 2 — Première démo hors ligne | Import de constats et de preuves synthétiques, validation de schéma, rapport Markdown | Une commande documentée produit le même rapport depuis un clone propre, sans service externe ni cible réseau |
| 3 — Qualité du noyau | Modules dédiés aux données, à la validation et au rapport ; erreurs utiles ; tests et CI | Tests de données invalides, preuves manquantes et export ; CI verte ; installation reproductible |
| 4 — Évaluation documentée | Jeu de référence synthétique, cas négatifs, métriques et comparaison de versions | Résultats reproductibles sur la qualité des rapports, les erreurs de validation, le temps et le coût ; limites publiées |
| 5 — Présentation portfolio | Démo courte, capture du résultat, schéma d'architecture, première release | Un recruteur comprend l'objectif, la contribution personnelle et les résultats en quelques minutes |

## Prochaine tranche proposée

Construire la démo du jalon 2 avec une petite CLI Python : lire un jeu de constats
synthétiques, contrôler les références de preuves, puis produire un rapport.
Le harness importé reste une référence pédagogique pendant cette tranche.
Le choix de Python suit les fichiers existants ; il ne fige pas la stack du
produit final.

Avant l'implémentation, convenir du schéma minimal, du format du rapport et de
trois exemples d'acceptation : entrée valide, preuve absente, entrée invalide.
Cette tranche permet de montrer du code original et testable sans attendre la
plateforme complète.

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

Une [revue des projets voisins](RELATED_PROJECTS.md) précise les références à
étudier, les licences annoncées et les éléments de conception utiles au premier
livrable. Le course pack a été retiré du dossier courant ; les références
pédagogiques conservées demandent encore une attribution vérifiée.
