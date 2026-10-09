# ARGOS — Statut du projet

**Status: ARCHIVED / SUPERSEDED.**

Remplacé par le [statut courant](../../project/STATUS.md).

Le contenu ci-dessous est conservé pour mémoire. Ses anciens statuts, décisions
et prochaines étapes ne définissent plus le corpus actif.

**Version :** 1.7\
**Statut :** canonique  
**Date de situation :** 9 octobre 2026\
**Phase :** premier livrable Argos Core hors ligne implémenté

---

## 1. Résumé

La vision générale d’Argos est approuvée. Le brainstorming global est terminé.

Argos est défini comme une plateforme professionnelle de cybersécurité  
offensive pilotée par IA, capable de conduire un pentest autorisé depuis le  
mandat jusqu’au retest.

Argos Core 0.1.0 implémente une première tranche originale : création de mission,
import de constats synthétiques, contrôle de preuves locales, revue humaine et
rapport Markdown déterministe. Les commandes fonctionnent avec la bibliothèque
standard Python. `doc/livrables/FIRST_DELIVERABLE.md` décrit la tranche acceptée par le
propriétaire et ses critères d'acceptation.

La plateforme complète du brief n'est pas implémentée.
`01_SCOPE_V0_ARGOS.md` version 1.0 reste `IN_PROGRESS`. Les supports pédagogiques
importés sont séparés du nouveau code et ne participent pas à la démo.

La demande du 7 octobre 2026 porte sur la préparation du dépôt pour GitHub et
les recruteurs, puis sur une progression par petites améliorations. Le nettoyage,
le README, la revue et une proposition de feuille de route sont ajoutés. La
présentation publique complète nécessite encore une décision sur l'historique des
missions et une clarification des droits de redistribution des imports restants.
La vérification distante confirme que le dépôt GitHub est déjà public. Le
propriétaire a retiré le course pack du dossier courant. Le nettoyage a été
publié et conserve l'historique existant ; la branche `feat/offline-reporting`
publiée au commit `422e2b9` inclut également les réalisations récentes.

Le front React/TypeScript et Discovery V0 sont réalisés comme prototypes
indépendants. Le front n'est raccordé ni à Argos Core ni à Discovery.
La [fiche Discovery](../../livrables/DISCOVERY_V0.md) conserve sa contradiction avec
l'exclusion de l'enrichissement commercial dans le draft V0 ; un rattachement
au produit reste à décider séparément.

La version 1.7 actualise l'inventaire des réalisations et les formulations sur
la publication, sans modifier les décisions produit ni le scope proposé.

Argos Arena est un projet séparé et n’est pas une dépendance d’Argos.

---

## 2. Travail terminé

### Premier livrable original — 7 octobre 2026

- `argos/` : commandes `init`, `import`, `validate`, `review` et `report` ;
- schéma structurel dans `schemas/assessment.schema.json` et contrôles des
  références, du scope et des preuves locales SHA-256 ;
- exemples synthétiques et rapport de référence dans `examples/offline/` ;
- revue humaine déclarée, sans confirmation automatique de vulnérabilité ;
- tests de contrat et d'intégration CLI ; commandes de développement dans `AGENTS.md` ;
- CI GitHub Actions sur Python 3.11, 3.12 et 3.13, avec actions officielles fixées
  à des commits précis et permissions de lecture ;
- autorisation du lot et contrat dans `doc/livrables/FIRST_DELIVERABLE.md`.
- laboratoire pédagogique déplacé hors du dépôt par le propriétaire ; retrait
  enregistré séparément, sans dépendance de la démo envers cet exercice.

### Préparation du dépôt — 7 octobre 2026

- suppression de 93 fichiers `Zone.Identifier` et ajout du `.gitignore` ;
- exclusion Git des missions locales, du sélecteur actif et des réglages personnels,
  avec conservation locale de ces données ;
- ajout de `README.md`, `doc/references/THIRD_PARTY_NOTICES.md`, `doc/suivi/REPOSITORY_REVIEW.md`
  et de la proposition `doc/suivi/ROADMAP.md` ;
- ajout d'un contrôle hors ligne de l'hygiène et de la syntaxe du dépôt ;
- vérification de l'intégrité Git et de la syntaxe des sources importées ;
- correction du manifeste : le scope V0 existe mais n'est pas validé.
- retrait des 40 fichiers du course pack encore présents dans l'index après
  suppression du dossier par le propriétaire ; exclusion du chemin pour les
  prochains imports ;
- ajout de `doc/references/RELATED_PROJECTS.md` avec sources primaires et licences annoncées ;
- vérification de la visibilité publique et de l'alignement avec `origin/main`
  avant préparation du commit.

### Accueil Web — 8 octobre 2026

- migration autorisée de l'accueil vers React, TypeScript strict et Vite ;
- thème sombre et loup–kraken conservés lors de la migration initiale,
  lisibilité et hiérarchie visuelle revues ;
- présentation « Front init » et mascotte d'origine ensuite restaurées dans
  React, comme décrit dans la [revue de l'accueil](../reviews/HOME_DESIGN_REVIEW.md) ;
- composants séparés par fonctionnalité, source de données explicite et logique
  de présentation indépendante de React ;
- dossier synthétique, rapport correspondant, consultation des constats,
  recherche, journal de session et chat à réponses locales ;
- tests unitaires et navigateur, compilation et job CI dédiés au front ;
- aucun raccordement au noyau, modèle IA ou moteur d'analyse ajouté ;
- contrat et fonctionnement du premier livrable Python hors ligne conservés.

### Organisation documentaire — 9 octobre 2026

- documentation regroupée dans `doc/` par type : produit, suivi, livrables,
  guides, interface et références ;
- sommaire dans [doc/README.md](../../README.md) et README de racine réduit aux
  points d'entrée ;
- guides du front et des exemples déplacés avec leurs liens corrigés ;
- chemin du livrable dans `AGENTS.md` et commandes de formatage du front adaptés ;
- noms et statuts des documents produit, contrats, code et données conservés.

### Décisions et travaux de juillet 2026

- vision inter-chats consolidée ;
    
- différence Argos / Argos Arena figée ;
    
- positionnement offensif professionnel validé ;
    
- anciens modes Learn, Lab et Operator abandonnés ;
    
- expériences Guidée et Experte validées ;
    
- autonomies Copilote, Supervisée et Autonome dans le scope validées ;
    
- pentest mandaté, bug bounty/VDP et évaluation contrôlée validés comme cadres  
    de mission ;
    
- bug bounty supervisé et soumission humaine validés pour la V0 ;
    
- dépendance à TryHackMe et Hack The Box écartée pour l’automatisation et les  
    benchmarks sans autorisation spécifique ;
    
- V0 interne simplifiée et découpée en cinq incréments ;
    
- chaînes Web/API, réseau/Linux et Windows/Active Directory rendues obligatoires  
    dans la V0 avec une profondeur limitée ;
    
- audit de code limité intégré à la chaîne Web/API de la V0 et AppSec approfondi  
    reporté à la V1 ;
    
- autonomie complète de la V0 réservée aux environnements contrôlés et  
    préautorisés ;
    
- Product Brief mis à jour en version 2.5 ;
    
- manifeste canonique mis à jour en version 1.1 ;
    
- présent statut mis à jour en version 1.1 ;
    
- ancien guide de travail déclaré retiré du corpus et absent du dépôt.
    

---

## 3. Décisions actives

### Produit

- un seul Argos, un seul moteur ;
    
- deux expériences : Guidée et Experte ;
    
- même moteur et même registre de capacités dans les deux expériences ;
    
- mêmes exigences de preuve et de qualité, avec davantage de protections et  
    moins de réglages exposés dans l’expérience Guidée ;
    
- possibilité de changer d’expérience pendant une mission ;
    
- option pédagogique indépendante ;
    
- laboratoire considéré comme environnement, pas comme mode.
    

### Missions

- parcours complet : autorisation, scope, objectifs, techniques, outils,  
    intensité, autonomie, plan, exécution, validation, preuve, rapport,  
    nettoyage et retest ;
    
- black box, grey box et white box ;
    
- tests authentifiés multi-rôles dans la cible professionnelle ;
    
- Scope Compiler et Scope Guard ;
    
- modèle vivant de la cible ;
    
- matrice de couverture ;
    
- Evidence Ledger ;
    
- validation indépendante des vulnérabilités ;
    
- registre des modifications et rollback.
    

### V0 interne

- fonctionnement local et mono-utilisateur ;
    
- réalisation ordonnée en cinq incréments : noyau sécurisé, Web/API,  
    réseau/Linux, Windows/Active Directory, puis qualification ;
    
- trois chaînes verticales obligatoires, représentatives et volontairement  
    étroites ;
    
- audit de code limité à la chaîne Web/API : lecture seule, secrets, dépendances,  
    règles SAST ciblées et rapprochement avec une validation dynamique ;
    
- Copilote et Supervisée utilisables sur les trois chaînes ;
    
- Autonome dans le scope limité aux environnements contrôlés, isolés et  
    préautorisés ;
    
- bug bounty limité à l’import des règles, au scope compilé, à l’exécution  
    supervisée et à la préparation d’un rapport soumis par un humain ;
    
- OSINT technique, référentiel minimal, catalogue d’outils réduit et interface  
    générique de benchmark.
    

### Sécurité

- contrôle déterministe et fermé par défaut du mandat, des exclusions, des  
    plafonds et des conditions d’arrêt, indépendant des agents et des modèles ;
    
- A4 explicitement autorisé et borné en mission professionnelle ;
    
- séparation classes d’action A0-A4 et exposition d’Argos E0-E2 ;
    
- control plane séparé des runners ;
    
- sécurité contre prompt injection, détournement d’agents et empoisonnement de  
    mémoire ;
    
- provenance, versions, hashes et permissions des outils dès la V0 ;
    
- SBOM complet avant pilote professionnel.
    

### Connaissances et modèles

- mémoire et preuves détenues par Argos ;
    
- indépendance vis-à-vis d’un fournisseur de modèle ;
    
- référentiel local-first sélectif ;
    
- cache progressif ;
    
- recherches officielles ciblées ;
    
- Knowledge Sync déterministe et distinct de l’agent OSINT ;
    
- aucune utilisation des données client pour l’entraînement sans consentement  
    explicite.
    

### Évaluation

- interface de benchmark indépendante ;
    
- Argos Arena facultatif ;
    
- benchmarks contrôlés et autorisés ;
    
- métriques de couverture, réussite, faux positifs, coût, temps humain,  
    reproductibilité, preuves, scope, nettoyage et retest.
    

---

## 4. Jalons

|Jalon|Objectif|État|
|---|---|---|
|Vision produit|Positionnement et décisions fondatrices|Terminé|
|Corpus canonique|Scope, sécurité, architecture, agents, outils, benchmark et tests|En cours|
|Premier livrable hors ligne|Mission, import, preuves, revue et rapport|Implémenté — tranche limitée|
|V0 interne|Noyau local et trois chaînes verticales réalisées en cinq incréments|Non commencé|
|Pilote professionnel|Missions supervisées à faible risque|Non commencé|
|MVP commercial|Utilisateurs externes et multi-client|Différé|
|V1|Couverture offensive approfondie|Différé|

---

## 5. Documents

|   |   |   |
|---|---|---|
|Document|Version|État|
|[00_PRODUCT_BRIEF_ET_PLAN_GLOBAL_ARGOS.md](../product/00_PRODUCT_BRIEF_ET_PLAN_GLOBAL_ARGOS.md)|2.5|Canonique|
|[CANONICAL_MANIFEST_ARGOS.md](CANONICAL_MANIFEST_ARGOS.md)|1.6|Canonique|
|[PROJECT_STATUS_ARGOS.md](PROJECT_STATUS_ARGOS.md)|1.7|Canonique|
|`GUIDE_TRAVAIL_ARGOS_AVEC_CHATGPT.md`|—|Retiré du corpus et absent du dépôt|
|[01_SCOPE_V0_ARGOS.md](../product/01_SCOPE_V0_ARGOS.md)|1.0|`IN_PROGRESS` — validation complète en attente|
|`doc/livrables/FIRST_DELIVERABLE.md`|1.0|Contrat du lot hors ligne accepté et implémenté|
|`02` à `15`|—|Planifiés|
|`AGENTS.md`|—|Actif pour le premier livrable hors ligne|
|`16` à `19`|—|Différés|

Le détail des dépendances se trouve dans  
`CANONICAL_MANIFEST_ARGOS.md`.

---

## 6. Questions ciblées restantes

Ces questions seront décidées dans les documents spécialisés :

- scénarios verticaux exacts de la V0 ;
    
- seuils chiffrés de réussite ;
    
- vulnérabilités représentatives et profondeur exacte des chaînes Web/API,  
    réseau/Linux et Windows/Active Directory ;
    
- langages, règles et outils exacts de l’audit de code limité ;
    
- stack technique ;
    
- stockage du Cyber Graph, des événements et des preuves ;
    
- modèles IA et stratégie de routage ;
    
- versions exactes et licences des outils ;
    
- limites de ressources des runners ;
    
- politique de rétention ;
    
- architecture du pilote professionnel ;
    
- disponibilité juridique et commerciale du nom Argos.
    

Elles ne nécessitent pas de reprendre un brainstorming général.

---

## 7. Prochaine étape autorisée

Le premier livrable hors ligne proposé dans `doc/suivi/ROADMAP.md` a été accepté et
implémenté. Sa fiche, son schéma et sa démonstration deviennent la base du prochain
lot : spécifier la persistance et la reprise de missions. Cette prochaine tranche
reste à définir avant implémentation. La démo ne remplace pas les cinq incréments
du scope V0 proposé, dont la validation complète reste à faire.

Le dépôt est déjà public. Les droits des imports et le traitement de l'historique
contenant les données de missions restent à clarifier. Le nettoyage publié
n'a pas purgé cet historique ; une purge reste une opération séparée à décider
explicitement.

La revue du scope doit confirmer :

1. les cinq incréments et leurs portes de validation ;
    
2. les trois scénarios verticaux obligatoires ;
    
3. les capacités incluses, optionnelles et différées ;
    
4. les entrées, sorties et états ;
    
5. les parcours Guidé et Expert ;
    
6. les niveaux d’autonomie et la restriction du mode Autonome ;
    
7. les règles A0-A4 et E0-E2 ;
    
8. les outils minimaux et l’audit de code limité ;
    
9. les exigences du Scope Compiler, du modèle de cible et de l’Evidence  
    Ledger ;
    
10. les exigences de sécurité prioritaires ;
    
11. les benchmarks et critères d’acceptation chiffrés ;
    
12. la définition de terminé de la V0 interne et la frontière explicite avec la  
    V1.
    

Pour la tranche hors ligne, les décisions de stack, de données, de sécurité et
de tests sont fixées dans `doc/livrables/FIRST_DELIVERABLE.md` ; le code et `AGENTS.md`
sont donc autorisés dans cette portée. Les capacités supplémentaires demandent
leur propre périmètre et leurs critères d'acceptation.

---

## 8. Risque principal

Le risque principal n’est plus un manque de vision, mais la dérive du périmètre  
pendant la rédaction du scope et l’implémentation.

La réduction de la V0 est désormais actée. Chaque capacité devra rester reliée à :

- un scénario vertical ;
    
- une preuve attendue ;
    
- un critère d’acceptation ;
    
- un benchmark ;
    
- une décision claire : obligatoire, optionnelle ou différée.
    

Aucune capacité V1 ne doit être réintroduite dans la V0 sans une décision  
canonique explicite et une analyse de son coût.
