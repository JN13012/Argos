# ARGOS — Manifeste canonique

**Version :** 1.3\
**Statut :** canonique  
**Date :** 7 octobre 2026

---

## 1. Objet

Ce manifeste identifie les documents qui font autorité pour Argos, leur version,  
leur statut, leur rôle et leurs dépendances.

Il évite :

- les copies concurrentes ;
    
- l’utilisation d’un document archivé ;
    
- les décisions fondées sur un ancien chat ;
    
- la création prématurée d’`AGENTS.md` ;
    
- la confusion entre Argos et Argos Arena.
    

Argos Arena possède sa propre documentation et n’appartient pas au corpus  
canonique d’Argos.

---

## 2. Statuts

|Statut|Signification|
|---|---|
|`CANONICAL`|Document actuel faisant autorité|
|`IN_PROGRESS`|Document en construction, non encore opposable|
|`PLANNED`|Document prévu mais non créé|
|`DEFERRED`|Document volontairement reporté|
|`ARCHIVED`|Historique conservé, sans autorité|
|`SUPERSEDED`|Remplacé par une version ou un document plus récent|
|`RETIRED`|Retiré du corpus et absent du dépôt actif|

---

## 3. Documents actuels

|   |   |   |   |
|---|---|---|---|
|Document|Version|Statut|Rôle|
|`00_PRODUCT_BRIEF_ET_PLAN_GLOBAL_ARGOS.md`|2.5|`CANONICAL`|Vision, positionnement, limites et trajectoire|
|`CANONICAL_MANIFEST_ARGOS.md`|1.3|`CANONICAL`|Versions, statuts, dépendances et ordre d’autorité|
|`PROJECT_STATUS_ARGOS.md`|1.3|`CANONICAL`|État courant, décisions récentes, travail restant et prochaine étape|
|`01_SCOPE_V0_ARGOS.md`|1.0|`IN_PROGRESS`|Proposition de scope V0 existante, en attente de validation explicite|

Les mises à jour 1.2 et 1.3 corrigent l'état des fichiers effectivement présents,
ajoutent les documents de préparation GitHub et enregistrent le retrait du course
pack ainsi que la revue des projets voisins. Elles ne valident pas le scope V0.

Documents de présentation et de préparation, sans autorité sur le scope produit :

- `README.md` : entrée du dépôt et distinction entre vision et code existant ;
- `docs/ROADMAP.md` : proposition de progression pour une démo et un portfolio ;
- `docs/REPOSITORY_REVIEW.md` : constat de préparation à la publication ;
- `THIRD_PARTY_NOTICES.md` : suivi de provenance des éléments importés.
- `docs/RELATED_PROJECTS.md` : sources d'inspiration et licences annoncées.

`GUIDE_TRAVAIL_ARGOS_AVEC_CHATGPT.md` est `RETIRED` : il est retiré du corpus  
actif, absent du dépôt et sans autorité. Il ne doit pas être recréé ni utilisé  
comme dépendance sans décision explicite.

---

## 4. Documents produit et techniques

|   |   |   |   |
|---|---|---|---|
|Ordre|Document|Statut initial|Dépendances minimales|
|1|`01_SCOPE_V0_ARGOS.md`|`IN_PROGRESS` — version 1.0 présente|Product Brief|
|2|`02_PARCOURS_MISSION_ET_UTILISATEURS.md`|`PLANNED`|Product Brief, Scope V0|
|3|`03_AUTORISATION_SCOPE_ET_RULES_OF_ENGAGEMENT.md`|`PLANNED`|Product Brief, Scope V0|
|4|`04_THREAT_MODEL_ET_SECURITE_ARGOS.md`|`PLANNED`|Product Brief, Scope V0, Autorisation/RoE|
|5|`05_CONFORMITE_DONNEES_ET_CONTRATS.md`|`PLANNED`|Scope V0, Autorisation/RoE, Threat Model|
|6|`06_ARCHITECTURE_TECHNIQUE.md`|`PLANNED`|Scope V0, Autorisation/RoE, Threat Model|
|7|`07_SYSTEME_MULTI_AGENTS_ET_WORKFLOWS.md`|`PLANNED`|Architecture, Scope V0, Threat Model|
|8|`08_MODELE_DE_DONNEES_ET_ATTACK_SURFACE_GRAPH.md`|`PLANNED`|Architecture, Parcours, Autorisation/RoE|
|9|`09_CONTRATS_API_ET_SCHEMAS.md`|`PLANNED`|Architecture, Agents, Modèle de données|
|10|`10_STRATEGIE_MODELES_IA.md`|`PLANNED`|Architecture, Agents, Threat Model|
|11|`11_CATALOGUE_OUTILS_PLAYBOOKS_ET_SDK.md`|`PLANNED`|Scope V0, Architecture, Agents, Autorisation/RoE|
|12|`12_PROTOCOLE_EVALUATION_ET_BENCHMARK.md`|`PLANNED`|Scope V0, Agents, Outils, Threat Model|
|13|`13_BACKLOG_EPICS_ET_STORIES.md`|`PLANNED`|Documents 01 à 12 nécessaires au lot planifié|
|14|`14_PLAN_DE_TEST_SECURITE_ET_QA.md`|`PLANNED`|Scope V0, Threat Model, Architecture, Benchmark|
|15|`15_PLAN_DE_DEPLOIEMENT_ET_OPERATIONS.md`|`PLANNED`|Architecture, Threat Model, Conformité, Tests|
|16|`AGENTS.md`|`PLANNED`|Scope, sécurité, architecture, backlog, tests, stack et commandes validés|

---

## 5. Documents commerciaux différés

|   |   |
|---|---|
|Document|Statut|
|`16_OFFRE_COMMERCIALE_ET_PRICING.md`|`DEFERRED`|
|`17_PLAN_PILOTES_CLIENTS.md`|`DEFERRED`|
|`18_SUPPORT_SLA_ET_GESTION_INCIDENTS.md`|`DEFERRED`|
|`19_ROADMAP_MODULES_ARGOS.md`|`DEFERRED`|

Ils seront commencés après validation de la V0 interne et avant le jalon auquel  
ils deviennent nécessaires.

---

## 6. Ordre d’autorité

Pour le produit :

1. autorisation, mandat et Rules of Engagement de la mission en cours ;
    
2. documents canoniques spécialisés dans leur domaine ;
    
3. `00_PRODUCT_BRIEF_ET_PLAN_GLOBAL_ARGOS.md` pour la vision et le  
    positionnement ;
    
4. `PROJECT_STATUS_ARGOS.md` pour l’état du travail ;
    
5. discussions et notes non encore intégrées ;
    
6. archives, qui n’ont aucune autorité.
    

Pour le développement :

1. limites légales, mandat et politiques de sécurité ;
    
2. `AGENTS.md` du dépôt lorsqu’il existera ;
    
3. critères d’acceptation de la story active ;
    
4. documents canoniques nécessaires au module ;
    
5. backlog et statut du projet.
    

Un document spécialisé peut préciser le Product Brief, mais ne peut pas  
modifier silencieusement une décision fondatrice.

---

## 7. Règles de version

- un document canonique conserve son nom stable ;
    
- une modification remplace le même fichier ;
    
- chaque nouvelle version met à jour sa date et son numéro ;
    
- le motif du changement est résumé dans le document ou son historique ;
    
- une ancienne version n’est pas copiée sous un nouveau nom dans le corpus  
    actif ;
    
- une contradiction doit être résolue dans les documents concernés et signalée  
    dans `PROJECT_STATUS_ARGOS.md` ;
    
- ce manifeste est mis à jour à chaque création, validation, archivage ou  
    remplacement de document ;
    
- le statut `CANONICAL` n’est attribué qu’après validation explicite ;
    
- `AGENTS.md` ne recopiera pas tout le corpus : il référencera les documents et  
    fixera les règles opérationnelles du dépôt.
    
- un document `RETIRED` absent du dépôt n’est pas présenté comme une archive  
    disponible.
    

---

## 8. Séparation d’Argos Arena

Les fichiers, décisions, scénarios et roadmaps d’Argos Arena :

- ne sont pas ajoutés à ce manifeste ;
    
- ne peuvent pas modifier implicitement le scope d’Argos ;
    
- ne constituent pas une dépendance pour le fonctionnement d’Argos ;
    
- peuvent être référencés uniquement comme environnement d’évaluation externe  
    autorisé.
    

---

## 9. Prochaine mise à jour

Après validation de `01_SCOPE_V0_ARGOS.md` :

- passer son statut à `CANONICAL` ;
    
- inscrire sa version ;
    
- mettre à jour `PROJECT_STATUS_ARGOS.md` ;
    
- confirmer les dépendances du document `02`.
