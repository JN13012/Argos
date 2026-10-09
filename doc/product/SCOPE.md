# Argos — Scope actif

**Status: CANONICAL — périmètre produit actif validé.**

Le développement actif porte sur **Argos OSINT**. La première verticale est
**Business Discovery + Website Opportunity** : par exemple, rechercher des
garages à Marseille, des boulangeries dans les Bouches-du-Rhône ou les artisans
d'un secteur.

## Objectif

1. Recevoir une recherche utilisateur.
2. Définir son scope : activité, zone, types d'entités et sources disponibles.
3. Découvrir le maximum d'entités correspondant au scope via ces sources.
4. Dédupliquer et résoudre les identités.
5. Persister les entités.
6. Enrichir progressivement leurs données.
7. Analyser les données selon différents objectifs.
8. Filtrer et classer les résultats.

```text
Discovery
→ Entity Resolution
→ Storage
→ Enrichment
→ Analysis
→ Ranking
```

## Collecter avant de sélectionner

« Trouve les garages susceptibles d'avoir besoin d'un meilleur site » définit
un scope de découverte et un objectif d'analyse distincts. Tous les garages
trouvés dans le scope via les sources interrogées doivent être conservés avant
analyse. L'intérêt supposé pour une offre ne doit provoquer aucun pré-filtrage
par l'IA.

La couverture dépend des sources accessibles et des bornes de collecte : aucune
exhaustivité territoriale n'est promise. Ces limites doivent être visibles.
Le classement sélectionne une vue des résultats sans supprimer les entités
collectées. Les règles techniques relèvent de l'[architecture OSINT](../architecture/OSINT.md).

## Hors scope immédiat

- Red complet et Defense.
- Agents autonomes complexes.
- SaaS, multi-tenant et infrastructure cloud.
- Frontend 3D avancé.
- Automatisation commerciale sortante.

## Prochain jalon

```text
Business Discovery
→ Website Resolution
→ Persistent Entity Store
→ Website Enrichment
→ Website Opportunity Analysis
```

[Discovery V0](../livrables/DISCOVERY_V0.md) constitue une première implémentation
partielle. Ce scope oriente son évolution ; il ne déclare ni ce jalon terminé,
ni ses contrats de données modifiés. L'état réel et la suite sont suivis dans le
[statut](../project/STATUS.md) et la [roadmap](../project/ROADMAP.md).
