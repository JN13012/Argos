# Argos — Scope immédiat

```text
Argos OSINT
↓
OSINT Foundation
↓
Business Discovery
```

Premier scénario réel à construire et valider : **trouver les garages de Marseille**.
La fondation devra représenter les entités, leurs identifiants, leurs observations,
les recherches et leur couverture, avec une persistance initiale envisagée en SQLite.

## Collect first, qualify later

```text
Scope → Discovery → Entity Resolution → Persistence
→ Enrichment → Analysis → Ranking
```

« Trouve les garages susceptibles d'avoir besoin d'un meilleur site Web »
définit un scope de découverte et un objectif d'analyse distincts. Le moteur
devra découvrir et persister les garages du scope avant d'évaluer une
opportunité. L'intérêt commercial supposé ne filtrera pas la collecte.

Le classement produira une vue des résultats sans supprimer les entités
collectées. La couverture dépendra des sources interrogées et des limites de
la recherche ; aucune exhaustivité territoriale ne sera promise.

## Tranches suivantes

1. Business Discovery : rechercher, résoudre les identités et persister.
2. Website Resolution : justifier l'association d'une entité à un site.
3. Website Enrichment : ajouter progressivement des observations sur le site.
4. Website Opportunity Analysis : interpréter et classer avec des raisons explicables.

Red, Defense, agents/harness de production, frontend, SaaS/cloud et
automatisation commerciale sortante sont hors scope immédiat.
Les [principes OSINT](OSINT.md) décrivent le moteur futur ; aucune de ces
capacités n'est implémentée dans cette passe documentaire.
