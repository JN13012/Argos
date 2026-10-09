# Projets proches d'Argos

**Consultation :** 7 octobre 2026. Cette revue décrit les positionnements et
licences annoncés par les projets ; aucun outil n'a été installé, exécuté ou
évalué. Les idées proposées pour Argos sont notre appréciation. Les chiffres de
performance publiés par les auteurs ne constituent pas une comparaison entre
produits ni une mesure pour Argos.

## Projets à étudier

| Projet et source primaire | Positionnement annoncé | Inspiration proposée pour Argos | Licence ou limite observée |
| --- | --- | --- | --- |
| [RedClaude / RedKraken](https://github.com/maajix/RedClaude) | Le README consulté présente un harness local pour missions Web/API sous le nom RedKraken | Diagnostic de configuration, séparation des données, tests de livraison | Licence non identifiée dans les sources consultées ; API du dépôt indisponible lors de la vérification, statut à confirmer |
| [Claude-Red](https://github.com/SnailSploit/Claude-Red) | Bibliothèque de skills spécialisés pour Claude | Organisation de la documentation en modules ciblés et suivi de provenance | MIT annoncée ; projet distinct de RedClaude |
| [Strix](https://github.com/usestrix/strix) | Outil de pentest IA, CLI, rapports et intégration CI/CD | Présentation des résultats, parcours développeur et exports | Apache-2.0 |
| [Shannon](https://github.com/KeygraphHQ/shannon) | Évaluation de sécurité des applications Web/API avec contexte du code source | Exemples de rapports, distinction des éditions, documentation des limites | AGPL-3.0 pour l'édition open source ; conditions commerciales distinctes |
| [PentAGI](https://github.com/vxcontrol/pentagi) | Système d'agents de pentest auto-hébergé | Interface opérateur, suivi des tâches et observabilité | MIT annoncée ; vérifier aussi `NOTICE`, dépendances et composants séparés |
| [PentestGPT](https://github.com/GreyDGL/PentestGPT) | Projet de pentest assisté par LLM associé à une publication USENIX Security 2024 | Documentation expérimentale et protocole d'évaluation reproductible | MIT ; utiliser le dépôt officiel identifié ici |
| [CAI](https://github.com/aliasrobotics/cai) | Framework de recherche en sécurité IA, désormais archivé | Référence historique pour organiser des expériences | Conditions mixtes : composants MIT et ajouts limités à la recherche ; ne pas traiter tout le dépôt comme MIT |
| [Red Clippy](https://github.com/CSPF-Founder/red-clippy) | Gestion de missions et de preuves, interface Web et MCP | Modèle actifs/observations/constats/preuves, couverture et suivi entre sessions | GPL-3.0 |
| [DefectDojo](https://github.com/DefectDojo/django-DefectDojo) | Gestion des vulnérabilités, déduplication, correction et rapports | Import de résultats, cycle de vie des constats, déduplication | BSD-3-Clause |

RedClaude et Claude-Red portent des noms proches mais sont des projets
différents. Pour RedClaude, les informations du README sont consultables via la
source Web, mais la disponibilité actuelle et la licence n'ont pas été
confirmées par l'API GitHub ; en faire une référence documentaire provisoire.
Pour CAI, le README et l'API GitHub indiquent l'archivage. Le README annonce
l'absence de nouvelles corrections et décrit des conditions de licence mixtes.

## Repères commerciaux

| Produit | Périmètre présenté par l'éditeur | Intérêt pour la vision |
| --- | --- | --- |
| [XBOW](https://docs.xbow.com/console/get-started/introduction/) | Tests automatisés Web/API et résultats associés à des preuves | Lisibilité des résultats et traçabilité |
| [NoScope](https://www.noscope.com/) | Pentest IA avec supervision humaine, contrôles de scope et approbations | Parcours de revue et contrôle opérateur |
| [NodeZero](https://horizon3.ai/nodezero/) | Évaluations internes, externes, cloud et identités, avec vérification des corrections | Restitution du risque et suivi des corrections |
| [Pentera](https://pentera.io/pentera-platform/) | Validation d'exposition sur réseau interne, actifs externes et cloud | Priorisation, gestion des corrections et mesure dans le temps |

Ce sont des repères concurrentiels pour la vision produit. Cette revue ne leur
attribue aucune autorisation de réutilisation de code.

## Choix proposé pour la prochaine tranche

Commencer par **Red Clippy et DefectDojo** pour le modèle de données, les preuves
et le suivi des corrections ; **Strix et Shannon** pour la lisibilité des
rapports ; **PentestGPT** pour la discipline d'évaluation.

Le premier livrable original proposé pour Argos reste une CLI hors ligne qui
valide des constats et preuves synthétiques puis génère un rapport. Mesurer
l'acceptation des entrées valides, le rejet des entrées invalides, les doublons et
la reproductibilité de l'export. Un jeu de démonstration et des critères
documentés permettent de montrer des contributions personnelles aux recruteurs.

## Réutilisation de code

Avant une reprise, identifier le fichier et son commit exact, lire sa licence
et les notices applicables, puis enregistrer son origine et les modifications
dans `doc/references/THIRD_PARTY_NOTICES.md`. Une licence annoncée pour un dépôt ne tranche pas
la licence de chaque dépendance ou de ses autres éditions. Les conditions GPL,
AGPL ou limitées à la recherche demandent une vérification adaptée au mode
d'intégration envisagé. Aucune reprise de code de ces projets n'a été effectuée
dans cette préparation.

Pour le portfolio, documenter explicitement les parties originales d'Argos, les
composants réutilisés et les résultats obtenus. Une inspiration d'interface ou de
structure reste distincte d'une copie de code ou de texte.
