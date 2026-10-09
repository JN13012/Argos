# Argos — Status

**Status: ACTIVE / CANONICAL — état de l'implémentation au 9 octobre 2026.**

## Current direction

La [vision](../product/VISION.md) organise Argos en OSINT, Red, Defense,
Agents / Harness et Interface. **OSINT est prioritaire**, avec Business
Discovery + Website Opportunity comme [scope actif](../product/SCOPE.md).

## Current implementation

- Argos Core : CLI hors ligne de missions, preuves, revue et reporting.
- [Discovery V0](../livrables/DISCOVERY_V0.md) : entreprises, enrichissement HTML
  limité, scores déterministes et snapshots SQLite/JSON.
- [Frontend React](../interface/FRONTEND.md) : accueil et dossier synthétique.
- `Harness/` : référence pédagogique séparée, provenance à clarifier.

Ces éléments ne constituent pas des modules Red, Defense ou agents de
production déjà implémentés.

## Active work

Documentation de l'architecture et de l'évolution du module OSINT. La
[référence OSINT](../architecture/OSINT.md) décrit la cible ; cette étape ne
modifie aucun code ni contrat existant.

## Known gaps

- Discovery reste sous `argos/discovery/` ; `argos/osint/` n'est pas appliqué.
- Website resolution limité aux sites déclarés et aux associations fournies.
- Sources et couverture OSINT limitées par les filtres et bornes du prototype.
- Snapshots par recherche, sans upsert global d'entités ni rafraîchissement partagé.
- Enrichissement avant sauvegarde du snapshot, à réordonner vers la cible.
- Harness de production non construit ; frontend non relié aux moteurs.

## Next step

Après validation de la documentation, restructurer progressivement Discovery
sous le module OSINT et améliorer Business Discovery / Website Opportunity.
La [roadmap](ROADMAP.md) ordonne ces étapes sans annoncer leur réalisation.
