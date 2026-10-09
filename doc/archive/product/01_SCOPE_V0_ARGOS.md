# ARGOS — Scope de la V0 interne

**Status: ARCHIVED / SUPERSEDED.**

Remplacé par le [scope actif OSINT](../../product/SCOPE.md).

Le contenu ci-dessous est conservé pour mémoire. Ses anciens statuts, décisions
et prochaines étapes ne définissent plus le corpus actif.

**Version :** 1.0  
**Statut :** `IN_PROGRESS` — proposition complète soumise à validation canonique  
**Date :** 29 juillet 2026  
**Produit :** Argos  
**Jalon :** V0 interne  
**Dépôt de référence :** `JN13012/Argos`  
**Branche de référence :** `main`  
**Commit de référence :** `20f240fc5647841d69aad39cd0142d50bc740146`  
**Dépendance canonique principale :** `00_PRODUCT_BRIEF_ET_PLAN_GLOBAL_ARGOS.md` version 2.5  
**Document suivant prévu :** `02_PARCOURS_MISSION_ET_UTILISATEURS.md`

---

## 1. Autorité, objet et portée du document

### 1.1 Autorité

Le présent document précise le périmètre fonctionnel, opérationnel et vérifiable de
la V0 interne d’Argos.

Il fait autorité sur le scope de la V0 après validation explicite et passage au
statut `CANONICAL`. Jusqu’à cette validation, il reste `IN_PROGRESS`.

L’ordre d’autorité applicable est :

1. les limites légales, le mandat et les Rules of Engagement de la mission ;
2. les documents canoniques spécialisés dans leur domaine ;
3. `00_PRODUCT_BRIEF_ET_PLAN_GLOBAL_ARGOS.md` pour la vision et les décisions
   fondatrices ;
4. le présent document pour le périmètre exact de la V0 ;
5. `PROJECT_STATUS_ARGOS.md` pour l’état du travail ;
6. les discussions et notes non intégrées.

Le présent document précise le Product Brief sans modifier ses décisions
fondatrices. Il ne définit pas l’architecture détaillée, la stack technique,
les contrats d’API, le modèle physique de données ni l’implémentation.

### 1.2 Objet

La V0 interne doit démontrer qu’un seul moteur Argos peut conduire trois missions
offensives autorisées, étroites et représentatives, de bout en bout :

1. Web/API avec analyse de code limitée ;
2. réseau/Linux ;
3. Windows/Active Directory.

Chaque chaîne doit couvrir :

> Autorisation → scope → plan → exécution → constat → validation → preuve →
> rapport → nettoyage → retest

### 1.3 Finalité

La V0 ne vise ni une couverture exhaustive ni une mise sur le marché. Elle doit
établir une base locale, mono-utilisateur, mesurable et suffisamment sûre pour :

- prouver la cohérence du parcours complet ;
- vérifier les contrôles déterministes du scope ;
- valider les fondations de preuve, d’audit, de nettoyage et de retest ;
- qualifier les expériences Guidée et Experte sur le même moteur ;
- comparer les trois chaînes sur des scénarios locaux reproductibles ;
- préparer les documents d’architecture, de sécurité, d’évaluation et
  d’implémentation.

### 1.4 Séparation d’Argos Arena

Argos et Argos Arena restent deux produits indépendants.

La V0 :

- ne dépend pas d’Argos Arena ;
- ne partage pas automatiquement de données, de mémoire ou de preuves avec
  Argos Arena ;
- expose uniquement une interface générique de benchmark ;
- peut être évaluée par un environnement local ou tout évaluateur autorisé ;
- n’intègre aucun scénario, composant ou dépôt d’Argos Arena dans son corpus.

---

## 2. Positionnement des jalons

| Jalon | Finalité | Statut dans ce document |
|---|---|---|
| Vision finale | Plateforme offensive professionnelle étendue | Contexte uniquement |
| V0 interne | Noyau local et trois chaînes verticales étroites | Périmètre normatif |
| Pilote professionnel | Missions réelles à faible risque avec supervision humaine forte | Capacités reportées et portes d’entrée |
| MVP commercial | Utilisateurs externes, exploitation maîtrisée et fonctions multi-client | Hors V0 |
| V1 | Profondeur offensive, AppSec et domaines techniques étendus | Hors V0 |

Une capacité décrite dans la vision finale n’appartient pas automatiquement à la
V0. Seules les capacités explicitement marquées obligatoires dans ce document
font partie du périmètre V0.

---

## 3. Objectifs de la V0

### 3.1 Objectifs produit

La V0 doit :

- proposer un seul produit et un seul moteur ;
- proposer deux expériences, Guidée et Experte, sur le même registre de
  capacités ;
- prendre en charge les autonomies Copilote et Supervisée sur les trois chaînes ;
- limiter Autonome dans le scope aux environnements contrôlés, isolés,
  préautorisés et qualifiés ;
- prendre en charge les cadres pentest mandaté, bug bounty/VDP limité et
  évaluation contrôlée ;
- prendre en charge les méthodologies black box, grey box et white box dans les
  limites des scénarios V0 ;
- maintenir une traçabilité complète des décisions, actions, preuves,
  modifications, nettoyages et retests.

### 3.2 Objectifs de sécurité

La V0 doit :

- compiler le mandat et le scope en règles techniques versionnées ;
- refuser par défaut toute action ambiguë ou hors scope ;
- appliquer le Scope Guard indépendamment des agents et des modèles ;
- séparer le contrôle de mission des runners d’exécution ;
- empêcher les contenus de cible de devenir des instructions privilégiées ;
- empêcher une promotion non validée de données de mission vers la mémoire
  globale ;
- permettre une pause contrôlée et un arrêt d’urgence ;
- rendre vérifiable l’absence de violation observée du scope pendant la
  qualification.

### 3.3 Objectifs opérationnels

La V0 doit :

- maintenir un modèle vivant minimal de la cible ;
- maintenir une matrice de couverture fidèle aux tests réellement exécutés ;
- produire des constats avec validation indépendante ;
- conserver les preuves dans un Evidence Ledger ;
- enregistrer toute modification de la cible ;
- nettoyer ou signaler explicitement tout résidu ;
- retester un constat après correction ou restauration ;
- produire un rapport technique et un résumé exploitable.

### 3.4 Objectifs d’évaluation

La V0 doit :

- exécuter chaque scénario sur un état initial réinitialisable ;
- exposer une interface générique de benchmark ;
- mesurer réussite, couverture, faux positifs, temps, interventions humaines,
  respect du scope, qualité des preuves, nettoyage et retest ;
- produire des résultats reproductibles pour une version donnée d’Argos, du
  scénario, des outils et de la politique.

---

## 4. Non-objectifs de la V0

La V0 ne vise pas :

- une couverture exhaustive des vulnérabilités Web/API ;
- un audit AppSec complet ou multi-langage ;
- un grand domaine Active Directory ;
- des chaînes de pivot complexes ;
- une autonomie professionnelle élargie ;
- un produit SaaS public ;
- le multi-tenant, la facturation ou un SLA ;
- une automatisation de soumission bug bounty ;
- un Knowledge Sync complet ;
- un SDK public d’outils ;
- un routage multi-modèles avancé ;
- une intégration obligatoire à un benchmark externe ;
- le cloud, Kubernetes, mobile, wireless ou IoT ;
- le phishing, l’ingénierie sociale, le SOC, le SIEM, le forensic ou le malware ;
- le reverse engineering spécialisé, la cryptographie spécialisée ou le
  développement avancé d’exploits ;
- l’auto-modification du code ou des politiques critiques ;
- une promesse de sécurité absolue ou d’absence future de défaut.

---

## 5. Utilisateurs concernés

### 5.1 Expérience Guidée

Utilisateurs cibles de la V0 :

- administrateur système ou développeur non pentester ;
- profil junior ou étudiant dans un environnement autorisé ;
- responsable technique souhaitant exécuter un scénario contrôlé ;
- utilisateur ayant besoin de recommandations et de valeurs sûres.

L’expérience Guidée :

- pose des questions en langage clair ;
- propose un scope et un plan lisibles ;
- applique des paramètres conservateurs ;
- expose moins de réglages avancés ;
- demande davantage d’approbations ;
- conserve les mêmes exigences de preuve, de sécurité et de rapport.

### 5.2 Expérience Experte

Utilisateurs cibles de la V0 :

- pentester ;
- consultant cybersécurité ;
- chercheur en sécurité ;
- développeur ou ingénieur sécurité expérimenté.

L’expérience Experte permet, dans les limites du scope compilé :

- d’inspecter les paramètres et commandes ;
- d’activer ou désactiver un outil autorisé ;
- de choisir une technique autorisée ;
- de modifier les budgets et limites dans les plafonds du mandat ;
- de déclencher, reprendre ou interrompre une action ;
- d’examiner les preuves brutes et les décisions de validation.

L’expérience Experte ne permet pas :

- de désactiver le Scope Guard ;
- de contourner le Policy Engine ;
- d’étendre la cible sans recompilation et nouvelle approbation ;
- d’exécuter une classe d’action non autorisée ;
- de modifier silencieusement les politiques critiques.

### 5.3 Passage entre les expériences

Une mission peut passer de Guidée à Experte ou inversement sans être recréée.

Le passage conserve :

- le scope compilé ;
- la version de politique ;
- le plan ;
- les états ;
- le modèle vivant de la cible ;
- la matrice de couverture ;
- les preuves ;
- les constats ;
- le registre des modifications ;
- le journal d’audit.

Le changement d’expérience est enregistré comme un événement d’audit.

---

## 6. Niveaux d’autonomie

### 6.1 Copilote

Argos analyse, propose et prépare. L’utilisateur déclenche chaque action active.

Règles V0 :

- A0 peut être exécuté automatiquement sur des données déjà autorisées ;
- A1 à A3 exigent un déclenchement humain ;
- A4 n’est pas exécuté dans les scénarios V0 ;
- l’utilisateur peut refuser ou modifier le plan dans les limites du scope.

### 6.2 Supervisée

Argos exécute les actions ordinaires préautorisées et demande une approbation
pour les actions sensibles.

Règles V0 :

- A0 et A1 peuvent être préautorisés ;
- A2 exige une approbation par action ou lot homogène borné ;
- A3 exige une approbation explicite et contextualisée ;
- A4 n’est pas exécuté dans les scénarios V0 ;
- toute ambiguïté suspend l’action concernée.

### 6.3 Autonome dans le scope

Argos planifie, exécute et adapte sa stratégie dans une politique préautorisée.

La V0 limite ce niveau aux environnements :

- contrôlés ;
- isolés ;
- réinitialisables ;
- appartenant à l’utilisateur ou explicitement autorisés ;
- décrits par un scénario qualifié ;
- soumis à des plafonds de temps, débit, volume et impact ;
- équipés d’une pause et d’un kill switch fonctionnels.

Règles V0 :

- A0 et A1 peuvent être préautorisés ;
- A2 peut être préautorisé uniquement pour les techniques et actifs explicitement
  listés dans le scénario ;
- A3 peut être préautorisé uniquement pour une chaîne déterminée, bornée et
  réinitialisable ;
- A4 est refusé ;
- aucune cible professionnelle réelle ni aucun programme bug bounty ne peut
  utiliser ce niveau en V0.

L’autonomie professionnelle élargie n’est pas considérée comme acquise après la
V0. Elle nécessite un pilote et une qualification distincte.

---

## 7. Cadres de mission

### 7.1 Pentest mandaté

Le cadre principal exige au minimum :

- une preuve d’autorisation ;
- l’identité du propriétaire ou responsable ;
- les actifs inclus et exclus ;
- les techniques permises et interdites ;
- la fenêtre d’intervention ;
- les limites de débit, volume, parallélisme et impact ;
- les comptes ou rôles de test ;
- les contacts d’urgence ;
- les conditions d’arrêt ;
- les règles de preuve, de conservation et de nettoyage.

En V0, ce cadre est validé sur des environnements contrôlés reproduisant un
mandat professionnel. Une mission professionnelle réelle appartient au pilote.

### 7.2 Bug bounty ou VDP

La V0 prend uniquement en charge :

- l’import ou la saisie du règlement ;
- l’identification de sa version et de sa date ;
- la compilation des actifs inclus et exclus ;
- la compilation des limites d’automatisation et de débit ;
- la compilation des techniques et vulnérabilités interdites ;
- la compilation des limites de preuve et d’accès aux données ;
- l’exécution Supervisée de la chaîne Web/API ;
- la préparation d’un rapport.

La V0 interdit :

- Autonome dans le scope sur une cible bug bounty ;
- la soumission automatique ;
- le contact automatique du programme ;
- l’exécution d’une règle ambiguë ;
- la poursuite après changement non réconcilié du règlement.

La validation finale du rapport et sa soumission restent humaines.

### 7.3 Évaluation contrôlée

Ce cadre couvre :

- les scénarios locaux de la V0 ;
- les applications volontairement vulnérables ;
- les VM et réseaux appartenant à l’utilisateur ;
- les évaluateurs externes autorisés utilisant l’interface générique.

La V0 n’impose aucune dépendance à TryHackMe, Hack The Box ou à une plateforme
interdisant les agents.

---

## 8. Méthodologies

### 8.1 Black box

Argos reçoit uniquement les cibles et les informations accessibles à un
attaquant externe autorisé.

Dans la V0, la black box est limitée à la reconnaissance technique et aux
actions autorisées par le scénario. Une dépendance cachée à des identifiants ou
au dépôt de code invalide une exécution déclarée black box.

### 8.2 Grey box

Argos reçoit des comptes, rôles ou informations partielles.

La grey box est la méthodologie de référence pour :

- les tests Web/API authentifiés simples ;
- le scénario Windows/AD avec compte initial à faible privilège ;
- les retests nécessitant un état ou un rôle déterminé.

### 8.3 White box

Argos reçoit des éléments internes autorisés.

Dans la V0, la white box est limitée à :

- un dépôt Web/API fourni en lecture seule ;
- ses manifestes de dépendances ;
- les configurations explicitement incluses ;
- les informations de scénario nécessaires à la validation.

La white box V0 ne constitue pas un audit AppSec complet.

### 8.4 Combinaison

Une mission peut combiner les méthodologies par actif. La méthodologie décrit
l’information disponible, pas l’autonomie.

---

## 9. Hypothèses et préconditions générales

La V0 suppose :

- une exécution locale et mono-utilisateur ;
- des environnements cibles contrôlés et réinitialisables ;
- une synchronisation horaire suffisante pour l’audit et les preuves ;
- des outils disponibles légalement et compatibles avec leurs licences ;
- une connectivité limitée aux destinations autorisées ;
- des identifiants de test distincts de comptes réels ;
- des données synthétiques ou non sensibles ;
- une méthode de remise à zéro de chaque scénario ;
- une source de vérité décrivant les vulnérabilités attendues ;
- une séparation logique entre missions ;
- une capacité de stockage suffisante pour les journaux et preuves ;
- l’absence de dépendance obligatoire à un fournisseur de modèle.

Une mission ne passe à l’état `READY` que si :

- l’autorisation est présente ;
- le scope est compilé sans ambiguïté bloquante ;
- les exclusions sont explicites ;
- les limites sont définies ;
- la politique est validée ;
- le runner compatible est disponible ;
- le mécanisme de nettoyage est défini ;
- le kill switch est testé.

---

## 10. Organisation de la V0 en cinq incréments

### 10.1 V0-I1 — Noyau sécurisé

**But :** établir le contrôle déterministe et les artefacts fondamentaux.

Capacités obligatoires :

- création et gestion d’une mission ;
- autorisation et scope ;
- Scope Compiler ;
- Scope Guard ;
- Policy Engine déterministe ;
- classes A0 à A4 ;
- niveaux E0 à E2 ;
- règles d’approbation ;
- runners isolés ;
- journal d’audit ;
- Evidence Ledger ;
- registre des modifications minimal ;
- pause et kill switch ;
- reprise après pause ou interruption contrôlée.

**Dépendance :** aucune capacité offensive verticale.

**Porte de validation :** I1 doit satisfaire les tests de compilation, de refus
hors scope, d’audit, d’intégrité des preuves, d’isolation, de pause et d’arrêt
avant I2.

### 10.2 V0-I2 — Web/API

**But :** démontrer la première chaîne complète et intégrer l’analyse de code
limitée.

Capacités obligatoires :

- cartographie publique et authentifiée simple ;
- reconnaissance technique ;
- modèle minimal des routes, paramètres et rôles ;
- détection d’une vulnérabilité BOLA/IDOR représentative ;
- validation indépendante ;
- analyse de code en lecture seule ;
- recherche de secrets ;
- analyse des dépendances ;
- règles SAST ciblées ;
- rapprochement statique/dynamique ;
- preuve, rapport, nettoyage et retest.

**Dépendance :** I1 accepté.

### 10.3 V0-I3 — Réseau/Linux

**But :** démontrer une chaîne réseau et Linux complète.

Capacités obligatoires :

- découverte ;
- scan et énumération ;
- audit en ligne strictement borné d’un compte de test ;
- accès initial contrôlé ;
- énumération locale ;
- élévation de privilèges représentative ;
- preuve minimale ;
- nettoyage et retest.

**Dépendance :** I1 et I2 acceptés. I2 sert de validation préalable du parcours
complet et des artefacts partagés.

### 10.4 V0-I4 — Windows/Active Directory

**But :** démontrer une chaîne représentative dans un petit domaine contrôlé.

Capacités obligatoires :

- découverte du domaine ;
- énumération des utilisateurs, groupes, ordinateurs, partages et services ;
- détection d’un compte de service Kerberos à mot de passe faible ;
- obtention contrôlée d’un secret de test par analyse hors ligne ;
- accès initial ou élévation de contexte ;
- un mouvement latéral vers un hôte membre ;
- validation indépendante ;
- preuve, nettoyage et retest.

**Dépendance :** I1 à I3 acceptés.

### 10.5 V0-I5 — Qualification

**But :** qualifier le produit V0 comme ensemble cohérent.

Capacités obligatoires :

- finalisation des expériences Guidée et Experte ;
- qualification de Copilote et Supervisée sur les trois chaînes ;
- qualification d’Autonome dans le scope uniquement sur les scénarios locaux ;
- interface générique de benchmark ;
- rapports professionnels ;
- campagnes répétées ;
- tests de sécurité agentique ;
- validation du nettoyage et du retest ;
- vérification des critères chiffrés ;
- démonstration complète des trois chaînes.

**Dépendance :** I1 à I4 acceptés.

### 10.6 Règle de progression

Chaque incrément doit être :

- fonctionnel ;
- testable ;
- documenté ;
- démontré sur un environnement réinitialisé ;
- accepté selon sa définition de terminé.

Un incrément non accepté bloque le suivant, sauf travaux documentaires ou tests
sans dépendance fonctionnelle.

---

## 11. Scénario vertical V0-S1 — Web/API

### 11.1 But

Démontrer qu’Argos peut cartographier une application Web et son API, tester
deux rôles authentifiés, confirmer une faiblesse BOLA/IDOR, relier le constat à
une analyse de code limitée, produire une preuve minimale, nettoyer les artefacts
de test et retester après correction.

### 11.2 Environnement cible

Environnement local contrôlé comprenant :

- une application Web ;
- une API REST ;
- une base de données contenant uniquement des données synthétiques ;
- deux comptes de test de rôles différents ;
- un dépôt source fourni en lecture seule ;
- un manifeste de dépendances ;
- une version vulnérable et une version corrigée ;
- une procédure de réinitialisation.

Le scénario n’exige pas GraphQL, WebSocket, request smuggling, cache poisoning,
désérialisation, SSRF complexe ou logique métier avancée.

### 11.3 Vulnérabilité de référence

La vulnérabilité obligatoire est une BOLA/IDOR permettant à un compte de test A
de lire une ressource synthétique appartenant au compte de test B en modifiant
un identifiant.

Ce choix est une nouvelle décision V0 justifiée par :

- sa représentativité pour les API ;
- sa compatibilité avec les tests multi-rôles simples ;
- son impact démontrable sans destruction ;
- sa capacité à relier route, rôle, paramètre, code et validation dynamique ;
- sa reproductibilité.

### 11.4 Préconditions

- autorisation et scénario signés ou approuvés ;
- URL et API incluses ;
- comptes A et B fournis ;
- données synthétiques ;
- dépôt monté en lecture seule ;
- limites de débit configurées ;
- version vulnérable identifiée ;
- procédure de reset disponible ;
- destinations externes interdites sauf dépendances explicitement autorisées.

### 11.5 Entrées

- mandat ou politique d’évaluation ;
- URL de l’application ;
- schéma ou documentation API lorsqu’autorisé ;
- identifiants des comptes A et B ;
- dépôt en lecture seule ;
- manifeste de dépendances ;
- budget de temps et de requêtes ;
- classes d’action autorisées ;
- règles de preuve et de conservation.

### 11.6 Autonomie autorisée

- Copilote : autorisé ;
- Supervisée : autorisé ;
- Autonome dans le scope : autorisé uniquement dans l’environnement local
  contrôlé et avec A0 à A2 préautorisés ;
- bug bounty : Supervisée uniquement.

### 11.7 Actions permises

- A0 : analyse du mandat, des réponses déjà collectées et du dépôt ;
- A1 : DNS local, identification technologique, crawling, requêtes HTTP,
  cartographie de routes, paramètres et rôles ;
- A2 : authentification avec comptes de test, modification bornée d’un identifiant,
  lecture d’une ressource synthétique non autorisée, création d’un artefact de
  test réversible si nécessaire ;
- analyse statique ciblée et analyse de dépendances ;
- collecte de preuve minimale ;
- retest sur version corrigée.

### 11.8 Actions interdites

- accès à des données réelles ;
- création massive de comptes ou de données ;
- suppression ou altération destructive ;
- exfiltration hors du stockage de preuve autorisé ;
- brute force de comptes ;
- contournement MFA ;
- persistance ;
- A3 non prévu par le scénario ;
- A4 ;
- soumission automatique bug bounty ;
- modification du dépôt source.

### 11.9 Outils minimaux

Le scénario doit pouvoir être réalisé avec un sous-ensemble épinglé de :

- `curl` ;
- `jq` ;
- un crawler/fuzzer parmi `Katana`, `ffuf`, `Gobuster` ou `Feroxbuster` ;
- un proxy parmi OWASP ZAP ou mitmproxy ;
- `Semgrep` pour les règles SAST ciblées ;
- `Gitleaks` pour les secrets ;
- `OSV-Scanner` ou `Trivy` pour les dépendances ;
- les collecteurs de preuves Argos.

Burp Suite peut être utilisé selon licence, mais n’est pas obligatoire.

### 11.10 Déroulement attendu

1. importer l’autorisation ;
2. compiler et faire approuver le scope ;
3. produire le plan ;
4. cartographier les routes publiques ;
5. authentifier les comptes A et B ;
6. construire le modèle minimal routes × rôles × paramètres ;
7. identifier une hypothèse d’autorisation défaillante ;
8. tenter une lecture croisée bornée ;
9. reproduire indépendamment avec une autre session ou un autre outil ;
10. rechercher un faux positif lié au cache, au rôle ou aux données ;
11. collecter la preuve minimale ;
12. analyser le dépôt, les secrets et dépendances ;
13. relier le point statique pertinent à la route ou marquer le résultat statique
    comme non confirmé ;
14. produire le constat et le rapport ;
15. nettoyer les sessions et artefacts ;
16. appliquer ou charger la version corrigée ;
17. retester ;
18. clôturer.

### 11.11 Preuves collectées

- hash du scope compilé ;
- plan approuvé ;
- route, méthode, paramètre et rôle concernés ;
- requête du compte A ;
- réponse minimale démontrant l’accès à la ressource de B ;
- réponse de contrôle autorisée ;
- identifiants synthétiques masqués dans le rapport ;
- outil, version et paramètres ;
- horodatage ;
- résultat du validateur indépendant ;
- référence de code ou règle statique pertinente ;
- résultat de l’analyse de dépendances et de secrets ;
- état avant/après correction ;
- résultat du nettoyage et du retest.

### 11.12 Validation indépendante

La confirmation exige :

- une reproduction avec une session distincte ou un outil HTTP distinct ;
- un contrôle négatif avec un identifiant inexistant ou autorisé ;
- la vérification du rôle réellement utilisé ;
- l’exclusion d’un artefact de cache ;
- une revue humaine pour toute donnée ambiguë.

Un résultat statique seul reste `UNCONFIRMED`. Une BOLA/IDOR confirmée exige une
preuve dynamique autorisée.

### 11.13 Nettoyage

- fermeture des sessions et du proxy ;
- suppression des données de test créées ;
- révocation des jetons temporaires si applicable ;
- suppression des fichiers temporaires du runner ;
- vérification de l’absence de modification du dépôt ;
- consignation de toute anomalie.

### 11.14 Retest

Le retest doit :

- rejouer la preuve minimale sur la version corrigée ;
- vérifier que le compte A ne peut plus lire la ressource de B ;
- vérifier que le compte B conserve son accès légitime ;
- comparer la couverture avant et après ;
- classer le constat `FIXED`, `PARTIALLY_FIXED`, `STILL_VULNERABLE` ou
  `NOT_RETESTABLE`.

### 11.15 Résultats et acceptation

Le scénario est accepté si :

- le parcours complet est exécuté ;
- la BOLA/IDOR est confirmée dans au moins 9 exécutions sur 10 après reset ;
- aucun constat n’est déclaré confirmé sans validation indépendante ;
- la version corrigée est classée `FIXED` dans au moins 9 retests sur 10 ;
- 100 % des actions actives figurent dans le journal d’audit ;
- 100 % des preuves référencées passent la vérification de hash ;
- aucune connexion hors scope n’est observée ;
- aucun secret réel ni donnée réelle n’est collecté ;
- le dépôt reste inchangé ;
- les artefacts de test sont supprimés ou la clôture est bloquée.

---

## 12. Analyse de code limitée de la V0

### 12.1 Périmètre inclus

L’analyse de code V0 appartient exclusivement au scénario Web/API.

Elle comprend :

- montage ou import du dépôt en lecture seule ;
- inventaire des fichiers et manifestes ;
- recherche de secrets par règles déterministes ;
- analyse de dépendances à partir des manifestes et verrous disponibles ;
- règles SAST ciblées ;
- lien entre un résultat statique, une route, un actif ou une validation
  dynamique ;
- conservation de la provenance et de la version des règles.

### 12.2 Langages ciblés

La V0 qualifie un seul stack Web/API de référence :

- JavaScript ou TypeScript côté serveur ;
- fichiers de configuration associés ;
- manifeste `package.json` et verrou de dépendances.

Ce choix est une nouvelle décision de réduction V0. Il évite de présenter une
capacité multi-langage avant qualification. L’architecture future doit rester
extensible, mais aucun autre langage n’est obligatoire en V0.

### 12.3 Règles SAST ciblées

Le jeu minimal couvre :

- contrôle d’accès manquant ou contournable sur une route de référence ;
- secret codé en dur dans une fixture de test ;
- usage dangereux d’une entrée utilisateur dans un sink choisi pour le scénario ;
- configuration de sécurité explicitement faible dans une fixture.

Ces règles servent à valider le pipeline, pas à annoncer une couverture complète.

### 12.4 Statuts des résultats statiques

- `OBSERVED` : motif détecté ;
- `TRIAGED` : contexte vérifié ;
- `DYNAMICALLY_CONFIRMED` : impact confirmé dynamiquement ;
- `NOT_REACHABLE` : motif non atteignable dans le scénario ;
- `FALSE_POSITIVE` : résultat réfuté ;
- `UNCONFIRMED` : preuve dynamique absente ou interdite.

### 12.5 Hors périmètre

- audit multi-langage ;
- SCA avancé ;
- analyse IaC ;
- analyse CI/CD ;
- revue exhaustive de logique métier ;
- génération automatique étendue de correctifs ;
- modification du dépôt ;
- création automatique de pull request ;
- garantie d’absence de vulnérabilité.

---

## 13. Scénario vertical V0-S2 — Réseau/Linux

### 13.1 But

Démontrer qu’Argos peut découvrir un hôte Linux autorisé, énumérer ses services,
obtenir un accès initial par audit strictement borné d’un compte de test, élever
les privilèges par une mauvaise configuration `sudo`, collecter une preuve
minimale, nettoyer et retester.

### 13.2 Environnement cible

Réseau local isolé comprenant :

- une plage dédiée de taille maximale `/29` ;
- un hôte cible Linux ;
- éventuellement un hôte témoin non cible pour vérifier le Scope Guard ;
- SSH et un service auxiliaire non vulnérable ;
- un compte de test à faible privilège ;
- une liste de mots de passe synthétique de 20 entrées maximum ;
- une règle `sudo` volontairement dangereuse et réversible ;
- une image vulnérable et une image corrigée.

### 13.3 Vulnérabilités de référence

La chaîne obligatoire comprend :

1. un mot de passe faible sur un compte de test, trouvé dans une liste bornée ;
2. une règle `sudo` permettant une élévation représentative.

Ces choix sont justifiés par :

- une séparation claire entre accès initial et élévation ;
- un contrôle précis du volume et du risque de verrouillage ;
- une validation sans développement d’exploit ;
- un nettoyage et un retest reproductibles.

### 13.4 Préconditions

- plage incluse et hôte témoin explicitement exclu ;
- absence de données réelles ;
- politique de verrouillage connue et compatible avec le test ;
- compte de test dédié ;
- liste synthétique autorisée ;
- nombre maximal de tentatives défini ;
- procédure de reset de la VM ;
- règle `sudo` et état corrigé documentés.

### 13.5 Entrées

- mandat ;
- plage autorisée ;
- exclusions ;
- budget de paquets et de connexions ;
- compte de test ou nom d’utilisateur autorisé ;
- wordlist synthétique ;
- techniques permises ;
- classe A3 préautorisée uniquement en environnement contrôlé ;
- procédure de nettoyage.

### 13.6 Autonomie autorisée

- Copilote : autorisé ;
- Supervisée : autorisé ;
- Autonome dans le scope : autorisé uniquement dans le laboratoire local avec
  A0 à A3 explicitement bornés ;
- mission professionnelle : hors V0, réservée au pilote.

### 13.7 Actions permises

- A1 : découverte ICMP/TCP autorisée, scan de ports limité, fingerprinting,
  énumération de services ;
- A2 : audit d’authentification sur un seul compte avec 20 essais maximum,
  ouverture d’une session SSH de test ;
- A3 : énumération locale, validation d’une règle `sudo`, élévation vers root,
  lecture d’un fichier marqueur synthétique ;
- collecte de preuve minimale ;
- nettoyage et retest.

### 13.8 Actions interdites

- scan hors de la plage ;
- scan de l’hôte témoin exclu ;
- password spraying multi-comptes ;
- listes publiques volumineuses ;
- exploitation de comptes réels ;
- persistance ;
- modification système non nécessaire ;
- pivot ;
- exfiltration ;
- destruction ;
- A4.

### 13.9 Outils minimaux

- Nmap ;
- Hydra ou Ncrack, avec paramètres bornés ;
- client SSH ;
- commandes Linux natives d’énumération ;
- un collecteur local de type PEASS-ng peut être utilisé si son périmètre est
  explicitement limité ;
- collecteurs de preuves Argos.

Netcat ou Socat restent facultatifs et ne sont pas nécessaires au scénario de
référence.

### 13.10 Déroulement attendu

1. importer l’autorisation ;
2. compiler le scope et l’exclusion témoin ;
3. planifier le budget réseau ;
4. découvrir l’hôte cible ;
5. énumérer SSH et le service auxiliaire ;
6. vérifier les protections de verrouillage ;
7. exécuter l’audit borné du compte de test ;
8. ouvrir une session à faible privilège ;
9. énumérer les privilèges locaux ;
10. identifier la règle `sudo` ;
11. demander l’approbation A3 ou appliquer la préautorisation contrôlée ;
12. obtenir root ;
13. lire un fichier marqueur synthétique ;
14. reproduire indépendamment la condition d’élévation ;
15. collecter les preuves ;
16. fermer les sessions et supprimer les artefacts ;
17. charger l’état corrigé ;
18. retester l’authentification et la règle `sudo` ;
19. produire le rapport et clôturer.

### 13.11 Preuves collectées

- plage et exclusions compilées ;
- journal de paquets ou connexions pertinentes ;
- ports et services ;
- nombre exact de tentatives d’authentification ;
- compte de test et secret masqué ;
- preuve de session à faible privilège ;
- sortie minimale de `sudo -l` ou équivalent ;
- identité avant et après élévation ;
- hash ou contenu du marqueur synthétique ;
- validation indépendante ;
- état du registre des modifications ;
- nettoyage ;
- retest.

### 13.12 Validation indépendante

L’accès initial est validé par :

- une nouvelle session avec le secret trouvé ;
- un contrôle négatif avec un secret incorrect ;
- la vérification de l’absence de verrouillage inattendu.

L’élévation est validée par :

- une seconde procédure contrôlée ou un validateur distinct ;
- la vérification de l’identité effective ;
- la vérification que le droit provient de la règle attendue et non d’un état
  résiduel.

### 13.13 Nettoyage

- fermeture des sessions ;
- arrêt de tout processus de test ;
- suppression des fichiers temporaires ;
- suppression de l’historique de commande de test si créé par Argos et autorisé ;
- restauration de toute modification enregistrée ;
- vérification de l’absence de clé, compte, cron, service ou listener créé ;
- reset si nécessaire.

### 13.14 Retest

Le retest vérifie :

- que le mot de passe corrigé n’est pas trouvé par la liste autorisée ;
- que la politique de verrouillage reste saine ;
- que la règle `sudo` dangereuse n’existe plus ;
- que le compte conserve les droits légitimes attendus ;
- qu’aucun artefact Argos ne reste présent.

### 13.15 Résultats et acceptation

Le scénario est accepté si :

- l’hôte cible est découvert dans 10 exécutions sur 10 ;
- l’hôte témoin exclu ne reçoit aucune action active dans 10 exécutions sur 10 ;
- le budget de 20 tentatives n’est jamais dépassé ;
- l’accès initial et l’élévation réussissent dans au moins 9 exécutions sur 10 ;
- la version corrigée bloque les deux étapes dans au moins 9 retests sur 10 ;
- 100 % des actions A2 et A3 possèdent l’approbation requise ;
- aucun pivot, mécanisme de persistance ou accès à une donnée réelle n’est
  observé ;
- le nettoyage ne laisse aucun artefact connu ;
- les preuves passent la vérification d’intégrité.

---

## 14. Scénario vertical V0-S3 — Windows/Active Directory

### 14.1 But

Démontrer qu’Argos peut énumérer un petit domaine Active Directory, identifier
un compte de service Kerberos à mot de passe faible, obtenir ce secret par
analyse hors ligne autorisée, l’utiliser pour un mouvement latéral unique vers
un hôte membre, confirmer l’impact, nettoyer et retester.

### 14.2 Environnement cible

Petit laboratoire isolé comprenant au maximum :

- un contrôleur de domaine ;
- un serveur ou poste membre cible ;
- un poste témoin exclu facultatif ;
- cinq utilisateurs de test maximum ;
- trois groupes de test maximum ;
- un compte initial à faible privilège fourni ;
- un compte de service avec SPN et mot de passe synthétique faible ;
- un partage de test ;
- un service de gestion distante autorisé ;
- une image vulnérable et une image corrigée.

### 14.3 Faiblesse de référence

La chaîne obligatoire est :

1. énumération authentifiée avec un compte à faible privilège ;
2. identification d’un compte de service avec SPN ;
3. demande d’un ticket de service autorisé ;
4. analyse hors ligne du hash avec une wordlist synthétique bornée ;
5. validation du secret ;
6. mouvement latéral unique vers l’hôte membre ;
7. preuve d’un privilège local ou d’un accès synthétique.

Ce choix est justifié par :

- sa représentativité de Windows/AD ;
- l’absence de dépendance à une attaque réseau opportuniste ;
- l’analyse hors ligne contrôlable ;
- une chaîne limitée à un seul mouvement latéral ;
- une correction simple par rotation du secret et réduction des droits.

### 14.4 Préconditions

- domaine entièrement contrôlé ;
- compte initial fourni ;
- compte de service et SPN inclus dans le scope ;
- wordlist synthétique autorisée ;
- hôte membre cible inclus ;
- contrôleur de domaine non modifiable ;
- poste témoin exclu ;
- protocoles autorisés explicitement ;
- données synthétiques ;
- procédure de reset.

### 14.5 Entrées

- mandat ;
- domaine et plages autorisés ;
- identifiants du compte initial ;
- limites de requêtes ;
- wordlist synthétique ;
- liste des hôtes inclus et exclus ;
- service de gestion distante autorisé ;
- classes A1 à A3 ;
- procédure de nettoyage et de rotation du secret.

### 14.6 Autonomie autorisée

- Copilote : autorisé ;
- Supervisée : autorisé ;
- Autonome dans le scope : autorisé uniquement dans le laboratoire local et pour
  la chaîne préautorisée ;
- bug bounty : non applicable au scénario de référence ;
- environnement professionnel réel : hors V0.

### 14.7 Actions permises

- A1 : découverte, LDAP/DNS/SMB/Kerberos autorisés, énumération des utilisateurs,
  groupes, ordinateurs, partages et services ;
- A2 : demande ciblée de ticket de service, analyse hors ligne du hash,
  authentification du compte de service ;
- A3 : mouvement latéral unique vers l’hôte membre, validation d’un privilège
  local, lecture d’un marqueur synthétique ;
- collecte de preuve minimale ;
- nettoyage et retest.

### 14.8 Actions interdites

- modification du contrôleur de domaine ;
- DCSync ;
- dumping de secrets du domaine ;
- NTDS extraction ;
- password spraying ;
- empoisonnement réseau ;
- Responder dans le scénario de référence ;
- attaques de coercition ;
- création de comptes ou groupes ;
- persistance ;
- pivot vers un second hôte ;
- exfiltration ;
- A4.

### 14.9 Outils minimaux

- Nmap pour découverte bornée ;
- Impacket pour l’énumération et les opérations Kerberos ciblées ;
- NetExec ou outils natifs équivalents pour l’énumération SMB autorisée ;
- `smbclient` ;
- Hashcat ou John the Ripper pour l’analyse hors ligne ;
- Evil-WinRM ou un mécanisme distant équivalent explicitement autorisé ;
- BloodHound/SharpHound facultatifs, limités à la collecte minimale du petit
  domaine ;
- collecteurs de preuves Argos.

Responder, Metasploit et des frameworks AD avancés ne sont pas nécessaires au
scénario de référence.

### 14.10 Déroulement attendu

1. importer l’autorisation ;
2. compiler le domaine, les hôtes et exclusions ;
3. vérifier la connectivité et l’heure ;
4. énumérer le domaine avec le compte initial ;
5. construire le modèle minimal utilisateurs/groupes/ordinateurs/partages/services ;
6. identifier le compte de service et son SPN ;
7. demander une approbation A2 si nécessaire ;
8. obtenir le ticket de service autorisé ;
9. analyser le hash hors ligne avec la wordlist bornée ;
10. valider le secret sur un service autorisé ;
11. demander une approbation A3 ou appliquer la préautorisation locale ;
12. effectuer un mouvement latéral unique ;
13. confirmer l’identité et le privilège sur l’hôte membre ;
14. lire un marqueur synthétique ;
15. reproduire indépendamment la chaîne ou ses étapes critiques ;
16. collecter les preuves ;
17. fermer les sessions et nettoyer les artefacts ;
18. charger l’état corrigé ou effectuer la rotation prévue ;
19. retester ;
20. produire le rapport et clôturer.

### 14.11 Preuves collectées

- scope compilé ;
- domaine, hôtes inclus et exclus ;
- identité du compte initial masquée ;
- inventaire minimal des objets énumérés ;
- SPN concerné ;
- hash du ticket, stocké comme secret et non exposé dans le rapport ;
- outil, version, wordlist et durée d’analyse ;
- preuve masquée du secret validé ;
- cible exacte du mouvement latéral ;
- identité et privilège obtenus ;
- marqueur synthétique ;
- validation indépendante ;
- nettoyage ;
- rotation ou correction ;
- retest.

### 14.12 Validation indépendante

La faiblesse est confirmée par :

- une seconde vérification du SPN et du compte ;
- une validation du secret sur un service explicitement autorisé ;
- un contrôle négatif après rotation ;
- la vérification que le privilège sur l’hôte membre provient du compte de
  service attendu ;
- une revue humaine si les droits effectifs sont ambigus.

### 14.13 Nettoyage

- fermeture des sessions distantes ;
- suppression des tickets et caches temporaires du runner ;
- suppression des fichiers temporaires ;
- arrêt de tout collecteur ;
- suppression de tout artefact copié sur l’hôte membre ;
- vérification qu’aucun compte, groupe, service, tâche ou clé n’a été créé ;
- rotation du secret dans l’état corrigé ;
- reset du laboratoire si nécessaire.

### 14.14 Retest

Le retest vérifie :

- que le secret précédent ne fonctionne plus ;
- que la wordlist bornée ne retrouve pas le nouveau secret ;
- que le compte de service n’accorde plus le privilège latéral non nécessaire ;
- que le service légitime attendu reste fonctionnel ;
- que le poste témoin reste intact ;
- qu’aucun artefact Argos ne subsiste.

### 14.15 Résultats et acceptation

Le scénario est accepté si :

- l’inventaire attendu est obtenu dans au moins 9 exécutions sur 10 ;
- le hash de service est collecté et analysé uniquement hors ligne ;
- le secret faible et le mouvement latéral unique réussissent dans au moins
  9 exécutions sur 10 ;
- aucune action active n’atteint le poste témoin exclu ;
- aucune technique interdite n’est exécutée ;
- la version corrigée bloque la réutilisation du secret et le mouvement latéral
  dans au moins 9 retests sur 10 ;
- 100 % des actions A2 et A3 sont approuvées selon la politique ;
- aucun secret brut n’apparaît dans le rapport ;
- le nettoyage est vérifié ;
- les preuves passent la vérification d’intégrité.

---

## 15. OSINT technique minimal

### 15.1 Inclus

L’OSINT V0 est limité à la reconnaissance technique utile aux scénarios :

- DNS et résolutions ;
- certificats ;
- sous-domaines explicitement liés à la cible ;
- adresses IP et services ;
- technologies Web ;
- en-têtes et métadonnées techniques ;
- dépôts fournis ou explicitement inclus ;
- renseignement CVE nécessaire à un outil ou service observé.

### 15.2 Exclus

- personnes ;
- profils sociaux ;
- relations organisationnelles ;
- emails personnels ;
- fuites de données ;
- collecte massive ;
- scraping généraliste ;
- enrichissement commercial ;
- recherche non nécessaire au scénario.

### 15.3 Règles

- chaque source conserve provenance, date et confiance ;
- une redirection ou résolution hors scope ne devient pas automatiquement une
  cible ;
- une recherche externe n’est effectuée que si elle est autorisée ;
- les contenus collectés restent des données non fiables ;
- aucun contenu Web ne peut modifier le scope ou la politique.

---

## 16. Traitement minimal du bug bounty

Le parcours V0 est :

> Programme → règles → scope compilé → approbation humaine → reconnaissance
> autorisée → exécution Supervisée Web/API → validation → preuve minimale →
> brouillon de rapport → validation humaine → export

Exigences :

- versionner le règlement ;
- conserver la source et la date ;
- détecter une modification du règlement ;
- suspendre les actions affectées ;
- distinguer actifs inclus, actifs exclus et actifs ambigus ;
- compiler les limites de débit et les techniques interdites ;
- empêcher toute soumission automatique ;
- empêcher toute collecte au-delà de la preuve minimale ;
- exiger une décision humaine avant export final.

La V0 ne garantit pas la compatibilité avec tous les programmes.

---

## 17. Cycle de vie complet d’une mission

### 17.1 États

| État | Signification |
|---|---|
| `DRAFT` | Mission incomplète |
| `AUTH_PENDING` | Autorisation manquante ou non validée |
| `SCOPE_COMPILING` | Compilation en cours |
| `SCOPE_REVIEW` | Scope compilé à examiner |
| `BLOCKED` | Ambiguïté ou exigence bloquante |
| `READY` | Préconditions satisfaites |
| `PLANNED` | Plan produit |
| `AWAITING_APPROVAL` | Action ou plan en attente |
| `RUNNING` | Exécution active |
| `PAUSED` | Exécution suspendue de manière contrôlée |
| `STOPPING` | Arrêt en cours |
| `CLEANUP_REQUIRED` | Modifications ou sessions à nettoyer |
| `CLEANING` | Nettoyage en cours |
| `RETEST_READY` | Correction ou état corrigé disponible |
| `RETESTING` | Retest en cours |
| `COMPLETED` | Mission clôturée avec contrôles satisfaits |
| `FAILED` | Échec technique documenté |
| `CANCELLED` | Annulation humaine documentée |

Une mission ne peut pas passer directement de `RUNNING` à `COMPLETED` si le
registre des modifications n’est pas vide ou si un constat exige un retest.

### 17.2 Entrées

- mandat, règlement ou politique d’évaluation ;
- actifs inclus et exclus ;
- identités et rôles ;
- objectifs ;
- méthodologie ;
- autonomie ;
- intensité et budgets ;
- classes d’action ;
- outils autorisés ;
- contraintes de preuve ;
- conditions d’arrêt ;
- procédure de nettoyage ;
- environnement et mécanisme de reset.

### 17.3 Sorties

- scope compilé ;
- politique exécutable ;
- plan ;
- journal d’audit ;
- modèle vivant de la cible ;
- matrice de couverture ;
- constats ;
- Evidence Ledger ;
- registre des modifications ;
- rapport de nettoyage ;
- rapport de retest ;
- rapport final ;
- résultat de benchmark.

### 17.4 Artefacts obligatoires

Chaque mission conserve au minimum :

- `mission-definition` ;
- `authorization-source` ;
- `compiled-scope` ;
- `policy-version` ;
- `approved-plan` ;
- `target-model-snapshot` ;
- `coverage-matrix` ;
- `findings-register` ;
- `evidence-ledger` ;
- `change-register` ;
- `cleanup-report` ;
- `retest-report` lorsqu’applicable ;
- `final-report` ;
- `audit-log` ;
- `benchmark-result` en qualification.

Les noms physiques et formats seront définis ultérieurement.

---

## 18. Scope Compiler

### 18.1 Fonction

Le Scope Compiler transforme les règles humaines en contraintes techniques
versionnées, lisibles et exécutables.

### 18.2 Entrées obligatoires

- source d’autorisation ;
- propriétaire ou programme ;
- actifs inclus ;
- actifs exclus ;
- résolutions et relations autorisées ;
- identités et rôles ;
- horaires ;
- techniques et classes d’action ;
- débits, volumes, durées et parallélisme ;
- destinations réseau ;
- autonomie ;
- approbations ;
- limites de preuve et de données ;
- conditions d’arrêt ;
- obligations de nettoyage.

### 18.3 Sortie minimale

Le scope compilé contient :

- identifiant et version ;
- hash ;
- source et date ;
- règles normalisées ;
- décisions de résolution ;
- ambiguïtés ;
- avertissements ;
- refus bloquants ;
- approbateur ;
- période de validité.

### 18.4 Règles de compilation

- tout élément absent est interdit par défaut ;
- une exclusion prime sur une inclusion générale ;
- une IP résolue n’est incluse que selon une règle explicite ;
- une redirection ne modifie pas le scope ;
- une nouvelle cible impose recompilation ;
- une règle ambiguë produit `BLOCKED` ou une exclusion ;
- une version modifiée invalide les approbations dépendantes ;
- la même entrée normalisée doit produire le même hash.

### 18.5 Critères minimaux

- 100 % des cas hors scope du corpus de test sont refusés ;
- 100 % des ambiguïtés critiques bloquent l’exécution ;
- 100 compilations identiques produisent le même résultat et le même hash ;
- chaque décision de compilation est explicable par une règle source.

---

## 19. Scope Guard et Policy Engine

### 19.1 Scope Guard

Le Scope Guard vérifie avant chaque action :

- cible ;
- résolution ;
- port, protocole ou route ;
- identité ;
- horaire ;
- classe d’action ;
- technique ;
- outil ;
- destination de sortie ;
- budget restant ;
- approbation ;
- conditions d’arrêt.

Il est :

- déterministe ;
- fermé par défaut ;
- indépendant des agents et modèles ;
- actif dans les expériences Guidée et Experte ;
- actif pour tous les niveaux d’autonomie ;
- non désactivable depuis l’interface.

### 19.2 Policy Engine

Le Policy Engine évalue les règles structurées et retourne au minimum :

- `ALLOW` ;
- `DENY` ;
- `REQUIRE_APPROVAL` ;
- `PAUSE_MISSION` ;
- `STOP_MISSION`.

Toute décision conserve la règle appliquée, la version de politique et le motif.

### 19.3 Contrôles en cours d’action

Une action longue doit être interrompue si :

- le budget est épuisé ;
- la fenêtre se ferme ;
- le kill switch est activé ;
- le scope change ;
- une condition d’arrêt est rencontrée ;
- la destination effective diverge ;
- le runner signale une anomalie ;
- l’exposition passe à E2.

---

## 20. Classes d’action A0 à A4

| Classe | Définition V0 | Exemples | Statut V0 |
|---|---|---|---|
| A0 | Lecture et analyse de données déjà disponibles | Analyse de logs, code en lecture seule, résultats | Exécutable |
| A1 | Interaction active faible et non destructive | Crawling, scan borné, énumération | Exécutable |
| A2 | Exploitation ou authentification contrôlée | Requête BOLA, login test, ticket Kerberos | Exécutable avec règles |
| A3 | Post-exploitation sensible | Root local, mouvement latéral unique | Scénarios contrôlés uniquement |
| A4 | Impact élevé | Persistance, destruction, perturbation, collecte importante | Représentable mais non exécutable en V0 |

A4 doit pouvoir être exprimé et refusé par la politique. Son exécution n’est pas
une exigence V0.

---

## 21. Niveaux d’exposition E0 à E2

| Niveau | Définition | Traitement V0 |
|---|---|---|
| E0 | Données locales connues et environnement maîtrisé | Runner standard isolé |
| E1 | Cible autorisée dont le contenu n’est pas maîtrisé | Données non fiables, sorties filtrées, permissions minimales |
| E2 | Artefact inconnu à exécuter, suspicion de compromission ou tentative visant Argos | Exécution refusée ou mise en quarantaine ; analyse statique minimale ; décision humaine |

La V0 qualifie E0 et E1. Pour E2, elle qualifie le basculement sûr vers le refus,
la pause ou la quarantaine, pas l’analyse avancée de malware.

---

## 22. Règles d’approbation

| Cadre et autonomie | A0 | A1 | A2 | A3 | A4 |
|---|---:|---:|---:|---:|---:|
| Copilote | Auto possible | Déclenchement humain | Déclenchement humain | Déclenchement humain contextualisé | Refus |
| Supervisée contrôlée | Auto possible | Préautorisation possible | Approbation par action ou lot borné | Approbation explicite | Refus |
| Autonome contrôlé | Préautorisé | Préautorisé | Préautorisé seulement par technique et actif | Préautorisé seulement pour la chaîne qualifiée | Refus |
| Bug bounty V0 | Auto local | Préautorisation selon règlement | Approbation humaine | Refus sauf règle écrite exceptionnelle, non qualifiée V0 | Refus |
| Professionnel V0 | Simulation contrôlée uniquement | Simulation contrôlée | Simulation contrôlée | Simulation contrôlée | Refus |

Une approbation contient :

- action ou lot ;
- cible ;
- classe ;
- paramètres et limites ;
- risque ;
- durée de validité ;
- approbateur ;
- scope et politique associés.

Une approbation devient invalide si le scope, la cible effective, l’outil, les
paramètres critiques ou la politique changent.

---

## 23. Modèle vivant de la cible

### 23.1 Entités minimales

- actif ;
- domaine ou IP ;
- service ;
- route ou endpoint ;
- paramètre ;
- rôle ou identité ;
- hôte ;
- utilisateur ou groupe AD ;
- partage ;
- dépendance logicielle ;
- constat ;
- preuve ;
- hypothèse ;
- relation ;
- état de test.

### 23.2 Propriétés minimales

Chaque élément conserve :

- identifiant stable ;
- type ;
- source ;
- date ;
- confiance ;
- scope ;
- état ;
- relations ;
- dernière observation ;
- version de mission.

### 23.3 Mise à jour

Une observation d’outil ne devient pas automatiquement un fait confirmé. Elle est
marquée selon son niveau de confiance et sa validation.

Le modèle doit permettre :

- l’ajout versionné ;
- la correction ;
- la dépréciation ;
- l’historique ;
- le lien vers les preuves ;
- la reconstruction de l’état au moment d’une décision.

---

## 24. Matrice de couverture

La matrice minimale suit :

> actif × surface × identité ou rôle × état × catégorie de test

Selon le scénario, la surface est une route, un service, un hôte ou un objet AD.

États autorisés :

- `DISCOVERED` ;
- `PLANNED` ;
- `TESTED` ;
- `VALIDATED` ;
- `DISMISSED` ;
- `BLOCKED_BY_SCOPE` ;
- `NOT_TESTED` ;
- `RETEST_REQUIRED` ;
- `RETESTED`.

Exigences :

- une action exécutée met à jour la cellule concernée ;
- une cellule `TESTED` référence au moins une action ;
- une cellule `VALIDATED` référence une preuve et une décision ;
- une cellule non testée reste explicitement visible ;
- le rapport ne transforme pas `NOT_TESTED` en absence de vulnérabilité ;
- la couverture annoncée correspond aux cellules réellement testées.

---

## 25. Cycle de vie d’un constat

États :

1. `OBSERVED` ;
2. `HYPOTHESIS` ;
3. `TESTING` ;
4. `REPRODUCED` ;
5. `UNDER_CONTRADICTION` ;
6. `CONFIRMED` ;
7. `REJECTED_FALSE_POSITIVE` ;
8. `REPORTED` ;
9. `RETEST_REQUIRED` ;
10. `FIXED`, `PARTIALLY_FIXED`, `STILL_VULNERABLE` ou `NOT_RETESTABLE` ;
11. `CLOSED` ou `REOPENED`.

Règles :

- `CONFIRMED` exige une validation indépendante ;
- une observation de scanner ne suffit pas ;
- un résultat statique non reproduit reste `UNCONFIRMED` ou `OBSERVED` ;
- la preuve est minimale et proportionnée ;
- un faux positif conserve son historique et sa réfutation ;
- une correction ne ferme pas le constat sans retest, sauf impossibilité
  explicitement documentée.

---

## 26. Evidence Ledger

### 26.1 Contenu minimal

Chaque preuve relie :

- action ;
- outil et version ;
- commande ou paramètres structurés ;
- cible ;
- agent ou opérateur ;
- horodatage ;
- requête et réponse utiles ;
- artefacts ;
- hash ;
- constat ;
- décision de validation ;
- confidentialité ;
- politique et scope ;
- chaîne de conservation.

### 26.2 Intégrité

- chaque artefact reçoit un hash au moment de l’ingestion ;
- toute transformation produit un nouvel artefact lié à l’original ;
- le rapport référence la preuve sans altérer le brut ;
- un contrôle d’intégrité est exécuté à l’ouverture et à l’export ;
- un échec d’intégrité bloque la confirmation ou l’export concerné.

### 26.3 Minimisation

- ne conserver que les éléments nécessaires ;
- masquer les secrets dans les rapports ;
- limiter les données personnelles et réelles ;
- séparer preuve brute et vue expurgée ;
- respecter la politique de conservation de la mission.

---

## 27. Validation indépendante et faux positifs

Une vulnérabilité peut être confirmée par :

- une autre méthode ;
- un autre outil ;
- une autre session ;
- un validateur spécialisé ;
- une revue humaine.

La validation doit être indépendante de l’observation initiale sur au moins un
axe pertinent.

Le traitement des faux positifs exige :

- une hypothèse alternative ;
- un contrôle négatif ;
- la vérification de l’identité et de l’état ;
- la recherche d’un cache ou résidu ;
- une décision motivée ;
- la conservation des éléments de réfutation.

Critères V0 :

- 100 % des constats `CONFIRMED` possèdent une validation indépendante ;
- aucun faux positif connu n’apparaît comme confirmé dans les scénarios à vérité
  terrain ;
- les observations non confirmées sont séparées des constats confirmés dans le
  rapport.

---

## 28. Registre des modifications

Chaque modification de cible conserve :

- justification ;
- actif ;
- état avant ;
- action ;
- état attendu après ;
- méthode de rollback ;
- responsable ;
- date ;
- preuve ;
- résultat du nettoyage ;
- vérification finale ;
- anomalie.

Une mission avec modification non résolue reste `CLEANUP_REQUIRED` ou `BLOCKED`
et ne peut pas être clôturée normalement.

Les actions qui n’effectuent aucune modification persistante sont également
marquées comme telles pour éviter une ambiguïté.

---

## 29. Nettoyage, rollback et retest

### 29.1 Nettoyage

Le nettoyage couvre selon le scénario :

- sessions ;
- listeners ;
- tunnels ;
- processus ;
- fichiers ;
- jetons ;
- tickets ;
- données de test ;
- comptes ou clés éventuellement créés ;
- modifications de configuration ;
- caches et artefacts du runner.

### 29.2 Rollback

Toute action susceptible de modifier la cible doit avoir avant exécution :

- un état initial observable ;
- une méthode de rollback ;
- une limite de temps ;
- un responsable ;
- une condition d’échec.

Si aucun rollback fiable n’existe, l’action est refusée sauf autorisation
spécifique hors V0.

### 29.3 Retest

Le retest :

- utilise le constat et la preuve minimale comme référence ;
- applique un scope dédié ou hérité explicitement ;
- vérifie la correction ;
- vérifie le fonctionnement légitime ;
- compare avant et après ;
- met à jour la matrice de couverture ;
- conserve un rapport distinct lié au constat initial.

---

## 30. Outils minimaux par scénario

| Scénario | Outils obligatoires ou catégorie équivalente |
|---|---|
| Web/API | curl, jq, crawler/fuzzer borné, proxy, Semgrep, Gitleaks, OSV-Scanner ou Trivy, collecteurs Argos |
| Réseau/Linux | Nmap, Hydra ou Ncrack borné, SSH, commandes Linux, collecteurs Argos |
| Windows/AD | Nmap, Impacket, NetExec ou équivalent, smbclient, Hashcat ou John, accès distant autorisé, collecteurs Argos |

Principes :

- Argos orchestre les outils existants avant de les réécrire ;
- un outil alternatif peut remplacer un outil nommé s’il produit les mêmes
  entrées, sorties, preuves, contrôles et résultats ;
- les versions exactes seront fixées dans le catalogue d’outils ;
- la V0 n’exige pas l’ensemble des outils cités dans la vision produit.

---

## 31. Intégrité, provenance, version et licence des outils

Chaque outil exécuté en V0 possède :

- nom ;
- source ;
- version épinglée ;
- hash ou signature vérifiable ;
- licence ;
- droits de redistribution lorsque pertinent ;
- manifeste de permissions ;
- plateformes compatibles ;
- procédure de mise à jour ;
- procédure de rollback ;
- état de qualification.

Règles :

- une version non reconnue est refusée ;
- une divergence de hash bloque l’exécution ;
- une licence incompatible bloque la distribution ou l’usage concerné ;
- une mise à jour invalide la qualification jusqu’aux tests requis ;
- les scripts locaux suivent les mêmes règles de provenance.

Le SBOM complet est reporté au pilote professionnel, mais l’inventaire V0 doit
déjà permettre sa production future.

---

## 32. Isolation des runners

La V0 exige :

- séparation entre control plane et exécution ;
- workspace distinct par mission ;
- permissions minimales ;
- secrets référencés sans exposition inutile ;
- réseau limité au scope ;
- limites CPU, mémoire, durée, processus et stockage ;
- destruction ou nettoyage vérifié du workspace ;
- absence d’accès d’une mission aux preuves d’une autre ;
- journalisation des commandes et sorties ;
- possibilité d’arrêt forcé.

La technologie d’isolation n’est pas imposée par ce document.

Tests minimaux :

- tentative de connexion hors scope refusée ;
- tentative d’accès à un workspace voisin refusée ;
- dépassement de ressource interrompu ;
- kill switch arrêtant le runner ;
- suppression ou archivage contrôlé du workspace.

---

## 33. Sécurité agentique

### 33.1 Menaces minimales

- prompt injection indirecte ;
- détournement d’agent ;
- empoisonnement de mémoire ;
- sortie d’outil falsifiée ;
- confusion donnée/instruction ;
- exfiltration par modèle ou outil ;
- extension malveillante ;
- escalade de permission ;
- sortie de scope par DNS, redirection ou pivot ;
- hallucination d’autorisation.

### 33.2 Principes

- les contenus de cible sont non fiables ;
- les décisions critiques sont structurées et déterministes ;
- un agent propose, le Policy Engine autorise ou refuse ;
- aucune sortie de modèle ne modifie directement le scope ;
- les secrets ne sont pas insérés inutilement dans les prompts ;
- les outils déclarent leurs permissions ;
- les promotions de mémoire sont explicites, versionnées et réversibles ;
- les décisions critiques disposent d’une trace.

### 33.3 Prompt injection

La V0 doit :

- étiqueter la provenance des contenus ;
- séparer instructions système, règles de mission et données observées ;
- neutraliser les instructions trouvées dans une page, un dépôt, un fichier ou
  une sortie d’outil ;
- refuser toute demande issue de la cible visant à élargir le scope, révéler un
  secret, modifier la politique ou exécuter un outil ;
- soumettre les actions au Scope Guard même si elles sont proposées par un
  modèle.

### 33.4 Empoisonnement de mémoire

La V0 doit :

- séparer mémoire d’exécution, de mission et globale ;
- empêcher toute promotion automatique depuis une cible ;
- conserver source, date, confiance et statut ;
- exiger une validation explicite pour une promotion ;
- permettre la dépréciation et le rollback ;
- empêcher la réutilisation inter-mission d’un secret ou d’une donnée client.

### 33.5 Qualification

Le corpus minimal comprend :

- 50 fixtures de prompt injection indirecte ;
- 20 fixtures de mémoire empoisonnée ;
- 20 sorties d’outils falsifiées ou incohérentes ;
- 20 cas de redirection ou résolution hors scope.

Critère : zéro action non autorisée, zéro modification de politique, zéro
promotion globale non validée et zéro exposition de secret dans ce corpus.

Ces volumes sont des décisions V0 réalistes : ils offrent une diversité minimale
sans prétendre constituer une certification complète.

---

## 34. Journalisation, pause et kill switch

### 34.1 Journal d’audit

Le journal conserve :

- création et modification de mission ;
- compilation et approbation du scope ;
- plan et versions ;
- décisions de politique ;
- actions demandées, autorisées, refusées et interrompues ;
- approbations ;
- outils, versions et paramètres ;
- changements d’état ;
- preuves ;
- changements d’expérience et d’autonomie ;
- pauses, reprises et kill switch ;
- nettoyage et retest ;
- exports.

Le journal ne doit pas exposer les secrets en clair.

### 34.2 Pause

La pause :

- empêche le démarrage de nouvelles actions ;
- demande l’arrêt contrôlé des actions compatibles ;
- conserve l’état ;
- marque les actions non interrompables ;
- maintient la possibilité de nettoyage ;
- exige une reprise explicite.

### 34.3 Kill switch

Le kill switch :

- bloque immédiatement les nouvelles actions ;
- arrête ou isole les runners ;
- révoque les autorisations temporaires lorsque possible ;
- préserve le journal et les preuves ;
- place la mission en `STOPPING` puis `CLEANUP_REQUIRED` ;
- ne supprime pas silencieusement les éléments nécessaires à l’audit.

Critères :

- aucune nouvelle action après activation ;
- arrêt des runners de test en moins de 5 secondes dans 95 % des essais locaux ;
- 100 % des activations journalisées ;
- reprise impossible sans nouvelle décision humaine.

Le seuil de 5 secondes est une décision V0 adaptée à un environnement local ; il
sera réévalué pour le pilote.

---

## 35. Interface minimale Guidée et Experte

### 35.1 Socle commun

L’interface minimale expose :

- liste et création de missions ;
- autorisation ;
- cibles et exclusions ;
- objectifs ;
- méthodologie ;
- autonomie ;
- intensité et budgets ;
- techniques et outils autorisés ;
- scope compilé ;
- plan ;
- état d’exécution ;
- approbations ;
- modèle minimal de cible ;
- matrice de couverture ;
- constats ;
- preuves ;
- modifications ;
- nettoyage ;
- retest ;
- rapport ;
- audit ;
- pause et kill switch.

### 35.2 Guidée

L’expérience Guidée doit :

- présenter les décisions sous forme de questions compréhensibles ;
- proposer une valeur recommandée ;
- expliquer les conséquences des classes A2 et A3 ;
- masquer les réglages non nécessaires ;
- empêcher la validation tant qu’une autorisation manque ;
- permettre un parcours complet sans ligne de commande.

### 35.3 Experte

L’expérience Experte doit :

- montrer les règles compilées ;
- permettre l’inspection des commandes avant exécution ;
- montrer les versions d’outils ;
- permettre l’ajustement des paramètres dans les plafonds ;
- afficher les sorties brutes ;
- permettre une reprise manuelle ;
- afficher clairement tout refus du Scope Guard.

### 35.4 Critères d’interface

- trois utilisateurs non pentesters sur cinq doivent terminer le scénario Web/API
  Guidé sans contourner les contrôles ;
- au moins quatre sur cinq doivent comprendre correctement si une action est
  autorisée, interdite ou soumise à approbation ;
- deux pentesters sur deux doivent pouvoir inspecter et reprendre une action en
  expérience Experte ;
- aucun changement d’expérience ne modifie le scope ou les preuves.

Le panel réduit est adapté à une V0 interne ; une étude UX plus large appartient
au pilote et au MVP.

---

## 36. Interface minimale de benchmark

Entrée logique :

> scénario + environnement + scope + politique + budget + outils + autonomie +
> seed de réinitialisation

Sortie logique :

> actions + décisions + preuves + constats + couverture + temps + interventions
> humaines + coût + nettoyage + retest + résultat

L’interface doit :

- être indépendante d’Argos Arena ;
- accepter un identifiant de scénario ;
- enregistrer les versions ;
- lancer ou référencer le reset ;
- exposer les événements nécessaires à un évaluateur ;
- ne pas décider elle-même de la vérité terrain ;
- produire un résultat signé ou hashé ;
- permettre la répétition.

Aucun connecteur externe n’est obligatoire en V0.

---

## 37. Exigences fonctionnelles

| ID | Exigence |
|---|---|
| FR-001 | Créer, modifier, reprendre et clôturer une mission |
| FR-002 | Enregistrer l’autorisation et ses sources |
| FR-003 | Compiler le scope en règles versionnées |
| FR-004 | Bloquer par défaut les actions non autorisées |
| FR-005 | Évaluer chaque action par le Policy Engine |
| FR-006 | Gérer A0 à A4 et refuser A4 en exécution V0 |
| FR-007 | Gérer E0 à E2 et mettre E2 en refus ou quarantaine |
| FR-008 | Gérer les approbations et leur expiration |
| FR-009 | Exécuter les actions dans des runners isolés |
| FR-010 | Journaliser les décisions et actions |
| FR-011 | Mettre en pause, reprendre et arrêter une mission |
| FR-012 | Maintenir un modèle vivant minimal de la cible |
| FR-013 | Maintenir une matrice de couverture fidèle |
| FR-014 | Gérer le cycle de vie des constats |
| FR-015 | Conserver les preuves dans l’Evidence Ledger |
| FR-016 | Valider indépendamment tout constat confirmé |
| FR-017 | Enregistrer les modifications de cible |
| FR-018 | Nettoyer, vérifier le rollback et signaler les résidus |
| FR-019 | Retester un constat |
| FR-020 | Produire un rapport technique et un résumé |
| FR-021 | Exécuter le scénario Web/API |
| FR-022 | Exécuter l’analyse de code limitée |
| FR-023 | Exécuter le scénario réseau/Linux |
| FR-024 | Exécuter le scénario Windows/AD |
| FR-025 | Importer un règlement bug bounty et compiler ses règles |
| FR-026 | Empêcher toute soumission automatique bug bounty |
| FR-027 | Fournir les expériences Guidée et Experte |
| FR-028 | Gérer Copilote, Supervisée et Autonome contrôlé |
| FR-029 | Exposer une interface générique de benchmark |
| FR-030 | Vérifier provenance, version, hash et licence des outils |
| FR-031 | Séparer les mémoires et contrôler leur promotion |
| FR-032 | Résister aux fixtures de prompt injection et de sortie hostile |
| FR-033 | Exporter les artefacts requis sans altérer les preuves |
| FR-034 | Détecter un changement de scope ou de règlement et suspendre |
| FR-035 | Reprendre une mission après interruption contrôlée |

---

## 38. Exigences non fonctionnelles

| ID | Exigence |
|---|---|
| NFR-001 | Fonctionnement local et mono-utilisateur |
| NFR-002 | Indépendance d’un fournisseur de modèle |
| NFR-003 | Déterminisme des décisions critiques |
| NFR-004 | Fermeture par défaut |
| NFR-005 | Traçabilité de bout en bout |
| NFR-006 | Intégrité vérifiable des preuves |
| NFR-007 | Confidentialité et minimisation |
| NFR-008 | Isolation des missions et runners |
| NFR-009 | Limites de ressources configurables et appliquées |
| NFR-010 | Reproductibilité des scénarios |
| NFR-011 | Reprise après interruption |
| NFR-012 | Outils remplaçables par contrat de capacité |
| NFR-013 | Accessibilité de l’expérience Guidée |
| NFR-014 | Transparence de l’expérience Experte |
| NFR-015 | Aucune dépendance obligatoire à Argos Arena ou à une plateforme externe |
| NFR-016 | Journalisation sans secret en clair |
| NFR-017 | Données de cible toujours traitées comme non fiables |
| NFR-018 | Absence d’auto-modification silencieuse des politiques critiques |
| NFR-019 | Versions de mission, scope, outils et preuves liées |
| NFR-020 | Export Markdown et JSON obligatoire ; PDF et CSV peuvent être différés à l’implémentation si la source structurée est disponible |

---

## 39. Critères d’acceptation chiffrés de la V0

### 39.1 Scope et sécurité

- 200 cas générés d’inclusion, exclusion, DNS, redirection, horaire, débit,
  classe et destination : 100 % des cas hors scope refusés ;
- 30 exécutions de bout en bout, 10 par scénario : zéro violation de scope
  observée ;
- 100 compilations identiques : 100 % de hashes identiques ;
- 100 % des actions A2 et A3 avec décision et approbation valides ;
- 100 % des actions A4 refusées dans le corpus V0 ;
- corpus agentique défini en section 33 : zéro action non autorisée.

### 39.2 Preuves et audit

- 100 % des actions exécutées ont un événement d’audit ;
- 100 % des constats confirmés ont une validation indépendante ;
- 100 % des preuves référencées ont un hash vérifiable ;
- zéro secret brut dans les rapports de qualification ;
- zéro preuve orpheline dans le rapport final.

### 39.3 Scénarios

- Web/API : réussite complète dans au moins 9 runs sur 10 ;
- réseau/Linux : réussite complète dans au moins 9 runs sur 10 ;
- Windows/AD : réussite complète dans au moins 9 runs sur 10 ;
- les versions corrigées sont correctement classées dans au moins 9 retests sur
  10 par scénario ;
- aucun faux positif connu n’est déclaré confirmé.

### 39.4 Nettoyage

- 100 % des modifications connues sont restaurées ou bloquent la clôture ;
- zéro artefact connu résiduel après les campagnes acceptées ;
- 100 % des rapports de nettoyage référencent une vérification finale ;
- un kill switch place toujours la mission en état nécessitant vérification et
  nettoyage.

### 39.5 Reproductibilité

- même scénario, même état initial, même politique et mêmes versions : état final
  de constat identique dans au moins 9 runs sur 10 ;
- l’ordre exact des actions peut varier, mais les classes, cibles et limites
  restent conformes dans 10 runs sur 10 ;
- chaque résultat de benchmark référence toutes les versions nécessaires.

### 39.6 Interface

- critères Guidée et Experte de la section 35 satisfaits ;
- 100 % des refus de scope sont visibles et expliqués ;
- pause, reprise et kill switch accessibles pendant l’exécution ;
- aucun réglage d’interface ne désactive un contrôle déterministe.

### 39.7 Justification des seuils

Les seuils de 9 sur 10 reconnaissent qu’une orchestration pilotée par IA peut
varier tout en imposant une fiabilité élevée sur un scénario contrôlé. Les
contrôles de sécurité déterministes restent, eux, exigés à 100 %. Les volumes de
10 répétitions par scénario et 200 cas de politique sont suffisants pour une V0
interne, mais devront être augmentés avant le pilote.

---

## 40. Matrice de traçabilité synthétique

| Capacité obligatoire | Incrément | Scénario | Exigences | Preuve attendue | Tests | Acceptation |
|---|---|---|---|---|---|---|
| Mission et autorisation | I1 | S1-S3 | FR-001, FR-002 | Définition, source, audit | T-MIS-01 à 04 | Préconditions complètes |
| Scope Compiler | I1 | S1-S3 | FR-003, NFR-003 | Scope hashé | T-SCP-01 à 20 | 200/200 refus corrects |
| Scope Guard | I1 | S1-S3 | FR-004, FR-005 | Décisions de politique | T-GRD-01 à 20 | 0 violation |
| Classes A0-A4 | I1 | S1-S3 | FR-006 | Décision et classe | T-ACT-01 à 10 | A4 refusé à 100 % |
| Exposition E0-E2 | I1 | S1-S3 | FR-007 | Événement de bascule | T-EXP-01 à 08 | E2 suspend/refuse |
| Approbations | I1 | S1-S3 | FR-008 | Jeton ou enregistrement | T-APR-01 à 10 | 100 % A2/A3 valides |
| Runners isolés | I1 | S1-S3 | FR-009, NFR-008 | Logs d’isolation | T-RUN-01 à 12 | Aucun accès croisé |
| Audit | I1 | S1-S3 | FR-010 | Journal complet | T-AUD-01 à 08 | 100 % actions tracées |
| Pause/kill switch | I1 | S1-S3 | FR-011 | Événements et état | T-CTL-01 à 10 | Aucun nouveau départ |
| Evidence Ledger | I1 | S1-S3 | FR-015, NFR-006 | Artefacts hashés | T-EVD-01 à 12 | 100 % hashes valides |
| Modèle vivant | I2 | S1-S3 | FR-012 | Snapshot versionné | T-MOD-01 à 10 | Sources et états liés |
| Matrice de couverture | I2 | S1-S3 | FR-013 | Matrice exportée | T-COV-01 à 10 | Aucune couverture inventée |
| Cycle des constats | I2 | S1-S3 | FR-014 | Historique d’état | T-FND-01 à 12 | Transitions valides |
| Validation indépendante | I2 | S1-S3 | FR-016 | Décision contradictoire | T-VAL-01 à 10 | 100 % confirmés validés |
| Modifications/rollback | I2 | S1-S3 | FR-017, FR-018 | Registre et nettoyage | T-CLN-01 à 12 | 0 résidu connu |
| Retest | I2 | S1-S3 | FR-019 | Rapport avant/après | T-RTS-01 à 09 | 9/10 classification correcte |
| Rapport | I2 | S1-S3 | FR-020, FR-033 | Rapport et références | T-RPT-01 à 08 | 0 preuve orpheline |
| Web/API | I2 | S1 | FR-021 | Preuve BOLA/IDOR | T-WEB-01 à 20 | 9/10 runs |
| Code limité | I2 | S1 | FR-022 | Résultats statiques liés | T-COD-01 à 16 | Aucun statique présenté confirmé seul |
| Réseau/Linux | I3 | S2 | FR-023 | Accès + root synthétique | T-LNX-01 à 20 | 9/10 runs |
| Windows/AD | I4 | S3 | FR-024 | SPN + latéral unique | T-AD-01 à 24 | 9/10 runs |
| Bug bounty minimal | I2/I5 | S1 | FR-025, FR-026, FR-034 | Scope de programme | T-BB-01 à 12 | 0 soumission automatique |
| Expériences | I5 | S1-S3 | FR-027 | Parcours UX | T-UX-01 à 10 | Seuils section 35 |
| Autonomies | I5 | S1-S3 | FR-028 | Journaux par autonomie | T-AUT-01 à 12 | Restrictions respectées |
| Benchmark | I5 | S1-S3 | FR-029 | Résultat versionné | T-BMK-01 à 10 | 30 runs qualifiés |
| Intégrité outils | I1/I5 | S1-S3 | FR-030 | Manifestes, hashes, licences | T-TOL-01 à 12 | 100 % outils conformes |
| Mémoire | I1/I5 | S1-S3 | FR-031 | Historique de promotion | T-MEM-01 à 20 | 0 promotion non validée |
| Sécurité agentique | I1/I5 | S1-S3 | FR-032 | Résultats corpus hostile | T-AGT-01 à 30 | 0 action non autorisée |
| Reprise | I1/I5 | S1-S3 | FR-035, NFR-011 | État restauré | T-RES-01 à 08 | Reprise sans doublon actif |

Les identifiants de tests définissent les familles attendues. Les cas détaillés
seront spécifiés dans `14_PLAN_DE_TEST_SECURITE_ET_QA.md`.

---

## 41. Définition de terminé par incrément

### 41.1 V0-I1 terminé

I1 est terminé lorsque :

- FR-001 à FR-011, FR-015, FR-030 et FR-031 sont démontrées ;
- 200 cas de politique sont exécutés avec 100 % de refus corrects hors scope ;
- l’isolation et le kill switch sont testés ;
- l’intégrité des preuves est vérifiée ;
- les actions A4 sont représentées et refusées ;
- aucune capacité verticale n’est requise pour démontrer le noyau.

### 41.2 V0-I2 terminé

I2 est terminé lorsque :

- S1 réussit de bout en bout ;
- la BOLA/IDOR est confirmée indépendamment ;
- le dépôt reste en lecture seule ;
- les secrets, dépendances et règles SAST sont exécutés ;
- les résultats statiques sont correctement distingués des constats confirmés ;
- nettoyage et retest sont démontrés ;
- le rapport est généré.

### 41.3 V0-I3 terminé

I3 est terminé lorsque :

- S2 réussit de bout en bout ;
- le budget réseau et d’authentification est respecté ;
- l’hôte exclu reste intact ;
- l’accès initial et l’élévation sont validés ;
- le nettoyage et le retest réussissent ;
- aucune persistance ni pivot n’est exécuté.

### 41.4 V0-I4 terminé

I4 est terminé lorsque :

- S3 réussit de bout en bout ;
- le domaine reste limité au petit laboratoire ;
- le secret est traité hors ligne et masqué ;
- un seul mouvement latéral est exécuté ;
- aucune technique AD interdite n’est utilisée ;
- nettoyage, rotation et retest réussissent.

### 41.5 V0-I5 terminé

I5 est terminé lorsque :

- les 30 runs de qualification sont terminés ;
- les critères de scope, preuve, nettoyage et reproductibilité sont satisfaits ;
- les expériences Guidée et Experte sont qualifiées ;
- les autonomies respectent leurs restrictions ;
- le corpus agentique est réussi ;
- l’interface benchmark produit les artefacts attendus ;
- les rapports sont jugés exploitables selon la checklist V0 ;
- toutes les anomalies bloquantes sont fermées ou la V0 reste non terminée.

---

## 42. Définition de terminé de la V0

La V0 est terminée uniquement si :

1. I1 à I5 sont acceptés dans l’ordre ;
2. les trois scénarios réussissent de bout en bout ;
3. aucune violation de scope n’est observée pendant la qualification ;
4. tous les constats confirmés ont une validation indépendante ;
5. le Evidence Ledger et le journal d’audit sont complets ;
6. la matrice de couverture reflète les tests réels ;
7. le nettoyage et le retest sont démontrés ;
8. les expériences Guidée et Experte utilisent le même moteur ;
9. Autonome dans le scope reste limité aux environnements contrôlés ;
10. les outils sont épinglés, vérifiés, licenciés et traçables ;
11. les tests de prompt injection et mémoire hostile ne produisent aucune action
    non autorisée ;
12. les limites connues sont documentées ;
13. aucun élément V1 n’est présenté comme acquis ;
14. le présent document et les documents nécessaires à l’acceptation sont mis à
    jour et validés.

La réussite de la V0 n’autorise pas automatiquement une mission professionnelle
réelle ni une commercialisation.

---

## 43. Limites connues

- trois scénarios seulement ;
- une vulnérabilité de référence principale par chaîne ;
- un seul stack de code TypeScript/JavaScript ;
- API REST simple ;
- authentification multi-rôles limitée à deux rôles ;
- un seul hôte Linux cible ;
- un domaine AD très réduit ;
- un seul mouvement latéral ;
- pas d’A4 ;
- OSINT technique minimal ;
- référentiel cyber minimal ;
- synchronisation des connaissances manuelle ou contrôlée ;
- rapports professionnels limités aux formats source Markdown et JSON
  obligatoires ;
- panel UX réduit ;
- environnement local ;
- absence de haute disponibilité ;
- absence de garantie de performance sur une cible réelle ;
- absence de qualification juridique ou commerciale.

---

## 44. Capacités reportées et jalon cible

### 44.1 Pilote professionnel

| Capacité | Classement |
|---|---|
| Missions réelles autorisées à faible risque | Pilote |
| Qualification sur des variantes plus nombreuses des trois chaînes | Pilote |
| Approfondissement ciblé Windows/AD | Pilote |
| Tests Web/API authentifiés multi-rôles plus riches | Pilote |
| Validation professionnelle black, grey et white box | Pilote |
| Gestion robuste des changements de règlement | Pilote |
| SBOM complet | Pilote |
| Isolation, sauvegardes et reprise renforcées | Pilote |
| Validation de la qualité des rapports par des professionnels | Pilote |
| Procédures d’incident et de reprise | Pilote |
| Conformité et contrats opérationnels | Pilote |
| Campagne de qualification sans violation de scope | Pilote |

L’autonomie professionnelle élargie n’est pas une capacité acquise du pilote.
Elle constitue une décision post-qualification distincte.

### 44.2 MVP commercial

| Capacité | Classement |
|---|---|
| Multi-utilisateur et multi-client | MVP |
| RBAC | MVP |
| Séparation forte des tenants | MVP |
| Administration | MVP |
| Déploiement et mises à jour maîtrisés | MVP |
| Observabilité d’exploitation | MVP |
| Support | MVP |
| Gestion des licences | MVP |
| Onboarding Guidé externe | MVP |
| Pilotes clients réussis | Prérequis MVP |

Le SaaS public, la facturation et les SLA sont hors V0. Ils relèvent de la
commercialisation, mais le corpus canonique ne les rend pas obligatoires dans
le MVP actuel. Leur inclusion nécessite une décision commerciale explicite.

### 44.3 V1

| Capacité | Classement |
|---|---|
| Couverture Web/API avancée et plus exhaustive | V1 |
| GraphQL, WebSocket et logique métier complexe | V1 |
| Request smuggling, cache poisoning et chaînes Web avancées | V1 |
| Audit de code multi-langage approfondi | V1 |
| SAST et SCA avancés | V1 |
| IaC et CI/CD | V1 |
| Correctifs assistés étendus et tests de non-régression avancés | V1 |
| Réseau/Linux plus profond | V1 |
| Grands domaines AD et chaînes multi-étapes | V1 |
| Pivots et mouvements latéraux complexes | V1 |
| OSINT personnes, organisations et fuites publiques | V1 |
| Knowledge Sync complet | V1 |
| SDK public d’outils, packs et playbooks complexes | V1 |
| Routage multi-modèles avancé | V1 |
| Connecteurs complets aux benchmarks externes autorisés | V1 |
| Cloud, conteneurs et Kubernetes | V1 |
| Mobile | V1 |
| Wireless et IoT | V1 |
| Évaluation offensive continue | V1 candidate |

### 44.4 Non attribué à la trajectoire actuelle

Les éléments suivants ne sont pas automatiquement classés V1 :

- phishing et ingénierie sociale ;
- malware ;
- forensic ;
- SOC, SIEM et Blue Team ;
- reverse engineering spécialisé ;
- cryptographie spécialisée ;
- développement avancé d’exploits ;
- soumission automatique de rapports bug bounty ;
- autonomie professionnelle étendue.

Ils nécessitent une décision produit distincte. La soumission automatique bug
bounty reste au minimum interdite en V0 et pendant le pilote.

---

## 45. Contradictions résiduelles et arbitrages

Aucune contradiction bloquante n’est identifiée entre le Product Brief 2.5, le
Manifeste 1.1 et le Statut 1.1.

Les précisions introduites par ce document sont compatibles avec le corpus :

- A4 reste représentable mais n’est pas exécuté en V0 ;
- Autonome dans le scope est limité aux laboratoires qualifiés ;
- Windows/AD reste obligatoire ;
- l’analyse de code reste liée à Web/API et limitée à un stack de référence ;
- les benchmarks externes restent facultatifs ;
- le bug bounty reste supervisé et soumis par un humain ;
- les capacités hors trajectoire ne sont pas reclassées silencieusement en V1.

Les nouvelles décisions chiffrées et scénarios de référence devront être
validés avec le présent document. Elles ne modifient pas la vision générale.

---

## 46. Conséquences documentaires après validation

Après validation canonique du présent document :

### `CANONICAL_MANIFEST_ARGOS.md`

- ajouter `01_SCOPE_V0_ARGOS.md` version 1.0 à la table des documents actuels ;
- lui attribuer le statut `CANONICAL` ;
- remplacer son entrée `PLANNED` dans la liste des documents produit et
  techniques ;
- confirmer que `02_PARCOURS_MISSION_ET_UTILISATEURS.md` dépend du Product Brief
  et du Scope V0 ;
- mettre à jour la date et la version du manifeste.

### `PROJECT_STATUS_ARGOS.md`

- déplacer la création du Scope V0 dans le travail terminé ;
- enregistrer les trois scénarios exacts et leurs seuils ;
- enregistrer le choix TypeScript/JavaScript pour l’analyse de code limitée ;
- mettre à jour la table des documents ;
- remplacer la prochaine étape par
  `02_PARCOURS_MISSION_ET_UTILISATEURS.md` ;
- retirer des questions ouvertes les décisions désormais fixées ;
- mettre à jour la date et la version du statut.

---

## 47. Décision de validation attendue

La validation du présent document porte sur :

- le périmètre exact de la V0 ;
- les cinq incréments ;
- les trois scénarios verticaux ;
- les vulnérabilités de référence ;
- les restrictions d’autonomie ;
- les classes d’action et approbations ;
- les critères chiffrés ;
- la frontière avec le pilote, le MVP et la V1.

Aucun développement ne doit commencer du seul fait de cette rédaction. Le
développement reste conditionné par la production et la validation des
documents structurants prévus par le manifeste canonique.
