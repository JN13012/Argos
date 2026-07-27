# ARGOS — Statut du projet

**Version :** 1.0  
**Statut :** canonique  
**Date de situation :** 27 juillet 2026  
**Phase :** préparation de la documentation canonique avant développement

---

## 1. Résumé

La vision générale d’Argos est approuvée. Le brainstorming global est terminé.

Argos est défini comme une plateforme professionnelle de cybersécurité  
offensive pilotée par IA, capable de conduire un pentest autorisé depuis le  
mandat jusqu’au retest.

Le développement d’Argos n’a pas encore commencé. La priorité est de produire  
le corpus documentaire minimal qui permettra ensuite à Codex d’implémenter le  
projet avec des limites, des critères d’acceptation et des tests explicites.

Argos Arena est un projet séparé et n’est pas une dépendance d’Argos.

---

## 2. Travail terminé

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
    
- Product Brief mis à jour en version 2.4 ;
    
- manifeste canonique créé ;
    
- présent statut créé ;
    
- ancien guide de travail classé comme archive non canonique.
    

---

## 3. Décisions actives

### Produit

- un seul Argos, un seul moteur ;
    
- deux expériences : Guidée et Experte ;
    
- mêmes capacités, preuves et exigences de qualité dans les deux expériences ;
    
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
    

### Sécurité

- mandat, exclusions, plafonds et conditions d’arrêt non contournables ;
    
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
|V0 interne|Noyau local mono-utilisateur et scénarios verticaux|Non commencé|
|Pilote professionnel|Missions supervisées à faible risque|Non commencé|
|MVP commercial|Utilisateurs externes et multi-client|Différé|
|V1|Couverture offensive approfondie|Différé|

---

## 5. Documents

|   |   |   |
|---|---|---|
|Document|Version|État|
|`00_PRODUCT_BRIEF_ET_PLAN_GLOBAL_ARGOS.md`|2.4|Canonique|
|`CANONICAL_MANIFEST_ARGOS.md`|1.0|Canonique|
|`PROJECT_STATUS_ARGOS.md`|1.0|Canonique|
|`GUIDE_TRAVAIL_ARGOS_AVEC_CHATGPT.md`|2.0|Archivé, non canonique|
|`01_SCOPE_V0_ARGOS.md`|—|Prochaine création|
|`02` à `15`|—|Planifiés|
|`AGENTS.md`|—|À créer avant le développement, après les spécifications structurantes|
|`16` à `19`|—|Différés|

Le détail des dépendances se trouve dans  
`CANONICAL_MANIFEST_ARGOS.md`.

---

## 6. Questions ciblées restantes

Ces questions seront décidées dans les documents spécialisés :

- scénarios verticaux exacts de la V0 ;
    
- seuils chiffrés de réussite ;
    
- profondeur Windows/AD obligatoire dans la V0 ;
    
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

Créer `01_SCOPE_V0_ARGOS.md`.

Le document doit fixer :

1. les scénarios verticaux obligatoires ;
    
2. les capacités incluses et différées ;
    
3. les entrées, sorties et états ;
    
4. les parcours Guidé et Expert ;
    
5. les niveaux d’autonomie ;
    
6. les règles A0-A4 et E0-E2 ;
    
7. les outils minimaux ;
    
8. les exigences du Scope Compiler, du modèle de cible et de l’Evidence  
    Ledger ;
    
9. les exigences de sécurité prioritaires ;
    
10. les benchmarks et critères d’acceptation chiffrés ;
    
11. la définition de terminé de la V0 interne.
    

Ne pas commencer le code ni créer `AGENTS.md` avant d’avoir les décisions  
structurantes nécessaires.

---

## 8. Risque principal

Le risque principal n’est plus un manque de vision, mais une V0 trop large.

Chaque capacité devra donc être reliée à :

- un scénario vertical ;
    
- une preuve attendue ;
    
- un critère d’acceptation ;
    
- un benchmark ;
    
- une décision claire : obligatoire, optionnelle ou différée.