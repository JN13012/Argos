# Argos — Roadmap

**Status: ACTIVE — trajectoire proposée, sans engagement de délai.**

La progression suit le [scope actif](../product/SCOPE.md). L'existant et ses
limites sont décrits dans le [statut](STATUS.md) ; l'architecture OSINT cible
reste à appliquer progressivement.

| Phase | Résultat attendu | État |
| --- | --- | --- |
| 1 — Documentation / architecture | Corpus court, autorités claires, distinction cible / existant et revue documentaire | Étape actuelle |
| 2 — OSINT foundation | Migration progressive de Discovery, identités stables, observations et contrats de stockage | À réaliser après revue documentaire |
| 3 — Business Discovery | Requêtes à scope explicite, meilleure couverture des sources, résolution et persistance avant enrichissement | Prototype existant à faire évoluer |
| 4 — Website Resolution + Enrichment | Associations de sites justifiées, enrichissement progressif et réutilisation des données fraîches | Enrichissement HTML limité existant ; resolver à améliorer |
| 5 — Opportunity Analysis | Analyse Website Opportunity séparée, explicable et recalculable sans redécouverte | Scores du prototype à faire évoluer |
| 6 — AI orchestration | Interprétation de requêtes et pilotage des workflows disponibles par un harness commun | Futur |
| 7 — Red integration | Cadrage et intégration progressive de capacités Red autorisées | Futur, hors scope immédiat |
| 8 — Defense later | Définition des besoins puis des capacités défensives | Différé |

Chaque évolution d'implémentation devra définir son périmètre, son contrat et
ses vérifications avant de modifier les comportements existants. La stack
complète, les modèles IA et l'hébergement ne sont pas fixés prématurément.
