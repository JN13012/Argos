# ARGOS — Product Brief et plan global

**Status: ARCHIVED / SUPERSEDED.**

Remplacé par la [vision modulaire](../../product/VISION.md).

Le contenu ci-dessous est conservé pour mémoire. Ses anciens statuts, décisions
et prochaines étapes ne définissent plus le corpus actif.

**Version :** 2.5  
**Statut :** vision approuvée — spécification V0 en cours  
**Date :** 28 juillet 2026  
**Prochaine étape :** `01_SCOPE_V0_ARGOS.md`

---

## 1. Objet du document

Ce document fixe la vision, le positionnement, les limites, les principes  
fondateurs et la trajectoire de développement d’Argos.

Il constitue la référence produit de plus haut niveau. Les documents spécialisés  
préciseront le scope, les parcours, l’autorisation, la sécurité, l’architecture,  
les agents, les outils, les benchmarks, les tests et l’implémentation.

La version 2.5 conserve les décisions fondatrices de la version 2.4 et :

- définit une V0 interne volontairement resserrée, réalisée en cinq incréments ;
    
- rend obligatoires trois chaînes verticales limitées : Web/API, réseau/Linux et  
    Windows/Active Directory ;
    
- introduit un audit de code limité dans la chaîne Web/API de la V0 et reporte  
    l’AppSec approfondi à la V1 ;
    
- réserve l’autonomie complète de la V0 aux environnements contrôlés et  
    préautorisés ;
    
- limite le bug bounty de la V0 à l’import des règles, à la compilation du scope,  
    à l’exécution supervisée et à la préparation d’un rapport soumis par un  
    humain ;
    
- précise les méthodologies black box, grey box et white box ;
    
- corrige le statut de l’ancien guide de travail, retiré du corpus actif et  
    absent du dépôt.
    

Le statut « vision approuvée » signifie que la direction générale est figée.  
Les détails mesurables de la V0 restent à définir dans  
`01_SCOPE_V0_ARGOS.md`.

---

## 2. Définition d’Argos

> **Argos est une plateforme souveraine, extensible et pilotée par IA pour  
> conduire des pentests offensifs autorisés de bout en bout, depuis  
> l’autorisation et la définition du scope jusqu’aux preuves, au rapport, au  
> nettoyage et au retest.**

Argos doit :

- comprendre un mandat, un programme de bug bounty ou une politique  
    d’évaluation ;
    
- transformer ces règles en contraintes techniques exécutables ;
    
- cartographier la cible et maintenir un modèle vivant de sa surface  
    d’attaque ;
    
- planifier et exécuter les techniques autorisées ;
    
- orchestrer les meilleurs outils existants ;
    
- adapter sa stratégie aux résultats ;
    
- valider les vulnérabilités et rechercher les faux positifs ;
    
- chaîner les faiblesses lorsqu’une preuve d’impact supplémentaire est utile et  
    autorisée ;
    
- conserver des preuves auditables ;
    
- produire des restitutions professionnelles ;
    
- nettoyer les modifications créées pendant la mission ;
    
- retester les corrections ;
    
- améliorer ses stratégies à partir de benchmarks contrôlés.
    

Argos n’est pas :

- un simple scanner de vulnérabilités ;
    
- un chatbot donnant seulement des commandes ;
    
- une collection d’outils sans orchestration ;
    
- un cyber range ;
    
- une plateforme Blue Team, SOC ou DFIR dans son périmètre actuel ;
    
- un système autorisé à agir hors d’un mandat ou d’un règlement explicite.
    

---

## 3. Positionnement et ambition

Argos vise à réunir dans une seule plateforme :

- la profondeur Web/API attendue d’un pentest moderne ;
    
- la couverture réseau, Linux, Windows et Active Directory ;
    
- l’exploitation et la post-exploitation contrôlées ;
    
- un parcours complet allant du scope au retest ;
    
- une orchestration ouverte d’outils, de modèles, de scripts et de playbooks ;
    
- un fonctionnement local ou privé ;
    
- une expérience accessible aux non-spécialistes sans réduire la qualité du  
    résultat ;
    
- des preuves, décisions et actions entièrement traçables.
    

L’objectif « meilleur que les concurrents » est une ambition mesurable, pas une  
affirmation marketing acquise. Argos devra être comparé équitablement à des  
plateformes spécialisées telles que XBOW, NodeZero, Pentera ou NoScope, ainsi  
qu’à des pentesters humains et à un LLM seul.

La supériorité recherchée devra être démontrée sur :

- la couverture réellement testée ;
    
- le taux de vulnérabilités uniques confirmées ;
    
- le taux de faux positifs et de faux négatifs ;
    
- la réussite de chaînes d’attaque ;
    
- le temps total et le temps humain ;
    
- le coût ;
    
- la reproductibilité ;
    
- la qualité des preuves et des rapports ;
    
- l’absence de violation du scope observée pendant les campagnes de  
    qualification ;
    
- la capacité à fonctionner localement et à changer de modèle ou d’outil.
    

---

## 4. Argos et Argos Arena

Argos et Argos Arena sont deux produits indépendants.

|Argos|Argos Arena|
|---|---|
|Plateforme opérationnelle de pentest offensif|Cyber range d’entraînement et de benchmark|
|Travaille sur des cibles autorisées, des programmes ou des environnements contrôlés|Héberge et réinitialise des scénarios vulnérables|
|Produit constats, preuves, rapports, nettoyage et retests|Produit scores, métriques, traces et classements|
|Gère mandat, règles d’engagement, scope et risques|Gère scénarios, VM, réseaux, resets et évaluateurs|
|Fonctionne sans Argos Arena|Fonctionne sans Argos|
|Ne partage aucune donnée client par défaut|Ne reçoit aucune donnée client réelle|

Argos Arena peut appeler l’interface de benchmark d’Argos comme n’importe quel  
évaluateur autorisé. Cette intégration reste facultative.

Les deux produits ont :

- des dépôts séparés ;
    
- des interfaces séparées ;
    
- des bases de données séparées ;
    
- des déploiements séparés ;
    
- des feuilles de route séparées ;
    
- aucun partage automatique de mémoire, de preuves ou de données client.
    

---

## 5. Utilisateurs et expériences

Argos utilise un seul moteur de pentest et propose deux expériences  
d’utilisation.

### 5.1 Expérience Guidée

Utilisateurs visés :

- PME ou organisation sans équipe cyber spécialisée ;
    
- administrateur système ou développeur ;
    
- étudiant ou profil junior ;
    
- utilisateur souhaitant déléguer la complexité technique.
    

Argos :

- pose des questions en langage clair ;
    
- explique les risques métier ;
    
- recommande le scope, les objectifs et les limites ;
    
- sélectionne automatiquement techniques, outils et paramètres ;
    
- masque les détails inutiles ;
    
- demande les approbations nécessaires ;
    
- produit le même niveau de preuve et de rapport qu’en expérience Experte.
    

L’expérience Guidée utilise le même moteur et le même registre de capacités que  
l’expérience Experte. Elle conserve les mêmes exigences de preuve et de qualité,  
mais applique des valeurs sûres, davantage d’approbations et une exposition plus  
limitée des paramètres avancés.

### 5.2 Expérience Experte

Utilisateurs visés :

- pentesters ;
    
- consultants ;
    
- équipes Red Team ;
    
- chercheurs en sécurité ;
    
- cabinets et MSSP.
    

L’utilisateur peut :

- importer et ajuster les Rules of Engagement ;
    
- choisir ou interdire des techniques et outils ;
    
- modifier les paramètres ;
    
- inspecter et relancer les commandes ;
    
- sélectionner des agents ou des modèles ;
    
- importer des scripts, wordlists et playbooks ;
    
- examiner les résultats et preuves brutes ;
    
- construire ou modifier une chaîne d’attaque ;
    
- reprendre la main à tout moment.
    

Le Scope Guard et les contraintes du mandat restent actifs en expérience  
Experte.

### 5.3 Passage entre les expériences

Une mission peut passer de Guidée à Experte, ou inversement, sans être recréée.  
Le scope, les preuves, les tâches, le graphe et l’historique sont conservés.

---

## 6. Dimensions d’une mission

Les notions suivantes sont indépendantes et ne doivent pas être confondues sous  
le mot « mode ».

### 6.1 Expérience

- Guidée ;
    
- Experte.
    

### 6.2 Cadre de mission

- pentest mandaté ;
    
- bug bounty ou Vulnerability Disclosure Program ;
    
- environnement contrôlé d’évaluation ou de recherche.
    

### 6.3 Autonomie

#### Copilote

Argos analyse, planifie et prépare les actions. L’utilisateur déclenche  
l’exécution.

#### Supervisée

Argos exécute les actions ordinaires autorisées et demande une validation pour  
les catégories sensibles prévues par la politique.

#### Autonome dans le scope

Argos planifie, exécute et adapte sa stratégie dans une politique préautorisée.  
Le Scope Guard, les plafonds, les conditions d’arrêt, le journal d’audit et le  
kill switch restent toujours actifs.

### 6.4 Méthodologie

- **black box** : Argos reçoit uniquement les cibles et informations accessibles  
    à un attaquant externe autorisé, sans compte ni connaissance interne ;
    
- **grey box** : Argos reçoit des comptes, rôles, informations ou documents  
    partiels afin de tester un point de vue utilisateur, partenaire ou employé ;
    
- **white box** : Argos reçoit les éléments internes autorisés, tels que code  
    source, architecture, configurations, comptes et documentation, afin  
    d’effectuer une analyse plus profonde.

Une mission peut combiner ces méthodologies selon les actifs. Elles décrivent le  
niveau d’information fourni, pas l’autonomie d’Argos.
    

### 6.5 Intensité

- discrète ;
    
- standard ;
    
- intensive ;
    
- profil personnalisé.
    

L’intensité configure notamment le débit, le parallélisme, la profondeur,  
le volume de données, les horaires et la tolérance aux effets secondaires.

### 6.6 Option pédagogique

L’accompagnement pédagogique est une option d’affichage et d’explication, pas  
un mode produit. Argos peut :

- expliquer ses décisions ;
    
- donner des indices progressifs ;
    
- commenter les commandes et résultats ;
    
- produire des notes d’apprentissage.
    

Cette option est destinée aux environnements appartenant à l’utilisateur ou  
autorisant explicitement cet usage.

---

## 7. Cadres de mission

### 7.1 Pentest mandaté

Le pentest mandaté est le cadre principal.

Il exige :

- une preuve d’autorisation ;
    
- le propriétaire ou responsable de la cible ;
    
- les actifs inclus et exclus ;
    
- les techniques permises et interdites ;
    
- les horaires ;
    
- les limites de débit, volume et impact ;
    
- les comptes et rôles de test ;
    
- les contacts d’urgence ;
    
- les règles de preuve, de conservation et de nettoyage.
    

### 7.2 Bug bounty et VDP

Argos doit pouvoir importer ou saisir le règlement d’un programme puis  
compiler :

- les actifs autorisés et interdits ;
    
- les règles d’automatisation ;
    
- les limites de débit ;
    
- les en-têtes ou comptes d’identification ;
    
- les techniques interdites ;
    
- les vulnérabilités éligibles ou exclues ;
    
- les limites de preuve et d’accès aux données ;
    
- les règles de divulgation ;
    
- le format de rapport attendu ;
    
- la date et la version du règlement.
    

Si une règle est ambiguë, incompatible avec l’automatisation ou modifiée  
pendant la mission, Argos suspend les actions concernées.

Parcours bug bounty :

> Programme → règles → scope compilé → reconnaissance autorisée → recherche →  
> validation indépendante → preuve minimale → rapport → approbation humaine →  
> soumission

Pour la V0 interne et le pilote professionnel :

- le bug bounty reste supervisé ;
    
- la soumission est toujours humaine ;
    
- Argos n’envoie aucun rapport et ne contacte aucun programme automatiquement ;
    
- la preuve s’arrête dès que l’impact éligible est suffisamment démontré.
    

### 7.3 Environnement contrôlé d’évaluation

Ce cadre concerne :

- benchmarks open source ;
    
- environnements internes ;
    
- applications volontairement vulnérables ;
    
- VM et réseaux appartenant à l’utilisateur ;
    
- Argos Arena via une intégration facultative ;
    
- services autorisant explicitement l’évaluation d’agents.
    

Argos ne doit pas dépendre de TryHackMe, Hack The Box ou d’une plateforme  
interdisant les bots. Aucun connecteur autonome ou benchmark sur ces services  
n’est fourni sans autorisation écrite spécifique.

---

## 8. Parcours utilisateur de bout en bout

### 8.1 Démarrage

Depuis le dashboard, l’utilisateur peut :

- créer une mission ;
    
- reprendre une mission ;
    
- consulter les constats et preuves ;
    
- lancer un retest ;
    
- ouvrir la surface d’attaque ;
    
- accéder aux outils, playbooks, agents et connaissances.
    

### 8.2 Autorisation et règles d’engagement

L’utilisateur importe ou renseigne :

- mandat ou programme ;
    
- propriétaire et contacts ;
    
- environnement ;
    
- actifs inclus et exclus ;
    
- horaires ;
    
- techniques autorisées ;
    
- limites opérationnelles ;
    
- règles de confidentialité ;
    
- conditions d’arrêt et de nettoyage.
    

### 8.3 Cibles et identités

Argos enregistre :

- domaines et URL ;
    
- API ;
    
- IP, plages et réseaux ;
    
- applications ;
    
- dépôts de code, configurations et manifestes de dépendances autorisés ;
    
- systèmes Linux et Windows ;
    
- domaines Active Directory ;
    
- comptes de test ;
    
- rôles et niveaux de privilège ;
    
- environnements de production, préproduction ou test.
    

### 8.4 Objectifs

L’utilisateur choisit ce qu’Argos doit démontrer :

- cartographier ;
    
- énumérer ;
    
- rechercher des vulnérabilités ;
    
- compromettre un compte ;
    
- obtenir un accès initial ;
    
- élever les privilèges ;
    
- pivoter ;
    
- démontrer un accès aux données ;
    
- tester une logique métier ;
    
- auditer du code source et relier les constats à la surface exposée ;
    
- produire des preuves et un rapport ;
    
- retester des corrections.
    

### 8.5 Techniques

Les techniques sont sélectionnées séparément des outils :

- reconnaissance passive et active ;
    
- scan et énumération ;
    
- crawling et fuzzing ;
    
- tests d’authentification et d’autorisation ;
    
- analyse statique, dépendances, secrets et configurations ;
    
- injections ;
    
- exploitation ;
    
- audit de mots de passe ;
    
- élévation Linux ou Windows ;
    
- techniques Active Directory ;
    
- pivot et mouvement latéral ;
    
- preuve d’impact ;
    
- persistance ou perturbation seulement lorsqu’elles sont explicitement et  
    spécifiquement autorisées.
    

### 8.6 Outils

Argos peut sélectionner les outils automatiquement. En expérience Experte,  
l’utilisateur peut les activer, les désactiver et les configurer.

### 8.7 Intensité, autonomie et contrôles

La mission fixe :

- niveau d’autonomie ;
    
- débit et parallélisme ;
    
- profondeur ;
    
- volume maximal de données ;
    
- horaires ;
    
- approbations ;
    
- plafonds d’impact ;
    
- conditions de pause ou d’arrêt.
    

### 8.8 Plan

Argos produit un plan compréhensible indiquant :

- phases ;
    
- hypothèses ;
    
- techniques ;
    
- outils ;
    
- dépendances ;
    
- risques ;
    
- validations ;
    
- durée et coût estimés ;
    
- critères de réussite et d’arrêt ;
    
- étapes de nettoyage prévues.
    

### 8.9 Exécution

L’utilisateur peut suivre :

- actions et commandes ;
    
- cible exacte de chaque action ;
    
- agents et outils actifs ;
    
- progression ;
    
- résultats intermédiaires ;
    
- consommation de ressources ;
    
- approbations en attente ;
    
- registre des modifications ;
    
- pause et kill switch.
    

### 8.10 Validation

Chaque constat suit le cycle défini à la section 13.

### 8.11 Restitution

Argos produit :

- résumé dirigeant ;
    
- rapport technique ;
    
- preuves et procédure de reproduction ;
    
- priorités de correction ;
    
- export Markdown, PDF, JSON et CSV lorsque pertinent.
    

### 8.12 Nettoyage et retest

Argos :

- ferme les sessions, listeners et tunnels ;
    
- supprime les comptes, fichiers et artefacts créés ;
    
- annule les modifications prévues ;
    
- vérifie le rollback ;
    
- consigne tout élément impossible à restaurer automatiquement ;
    
- reteste les corrections ;
    
- compare l’état avant et après ;
    
- clôture la mission.
    

---

## 9. Capacités offensives

### 9.1 OSINT et surface d’attaque

- domaines, sous-domaines, DNS, certificats et IP ;
    
- ASN, services et technologies ;
    
- archives publiques et métadonnées ;
    
- dépôts publics et secrets exposés ;
    
- personnes, emails, organisations et relations ;
    
- fuites rendues publiques ;
    
- renseignement sur les vulnérabilités ;
    
- provenance, fraîcheur et niveau de confiance.
    

### 9.2 Réseau et infrastructure

- découverte d’hôtes ;
    
- scan et énumération de ports, services et protocoles ;
    
- fingerprinting de systèmes et versions ;
    
- mauvaises configurations ;
    
- validation de vulnérabilités ;
    
- exploitation autorisée ;
    
- accès initial ;
    
- segmentation et chemins réseau ;
    
- pivot et mouvement latéral.
    

### 9.3 Web et API

- crawling public et authentifié ;
    
- cartographie des routes, paramètres, rôles et états ;
    
- fichiers JavaScript et source maps ;
    
- REST, GraphQL et WebSocket ;
    
- authentification, sessions, jetons et MFA ;
    
- tests multi-rôles ;
    
- SQLi et NoSQLi ;
    
- XSS ;
    
- SSRF ;
    
- XXE ;
    
- SSTI ;
    
- LFI, RFI et path traversal ;
    
- injection de commandes ;
    
- upload de fichiers ;
    
- désérialisation ;
    
- IDOR et BOLA ;
    
- logique métier ;
    
- request smuggling ;
    
- cache poisoning ;
    
- erreurs de configuration, dépendances et secrets exposés ;
    
- chaînage et preuve d’impact.
    

### 9.4 Audit de code et sécurité applicative

Dans sa vision complète, Argos peut :

- importer un dépôt autorisé en lecture seule ;
    
- cartographier l’architecture, les routes, les contrôleurs, les autorisations et  
    les flux de données ;
    
- rechercher les secrets, dépendances vulnérables et configurations dangereuses ;
    
- orchestrer des analyses SAST, SCA et Infrastructure as Code ;
    
- examiner les défauts de logique métier et de contrôle d’accès ;
    
- relier un constat statique à une route, un actif et une validation dynamique ;
    
- réduire les faux positifs par analyse contradictoire ;
    
- proposer des correctifs et des tests de non-régression ;
    
- retester les corrections.
    

La V0 limite cette capacité à la chaîne Web/API : lecture seule, recherche de  
secrets, analyse de dépendances, règles SAST sur un petit nombre de langages et  
rapprochement avec une validation dynamique lorsque celle-ci est sûre et  
autorisée. L’AppSec multi-langage approfondi, l’IaC, le CI/CD et la génération de  
correctifs sont reportés à la V1.

### 9.5 Linux, Windows et Active Directory

- énumération locale et distante ;
    
- utilisateurs, groupes, partages, services et privilèges ;
    
- mauvaises configurations ;
    
- Kerberos et NTLM ;
    
- chemins d’attaque ;
    
- élévation locale ou de domaine ;
    
- mouvement latéral ;
    
- preuves et nettoyage.
    

### 9.6 Mots de passe et secrets

- audit en ligne contrôlé ;
    
- contrôle des limites et verrouillages ;
    
- analyse hors ligne de hashes ;
    
- wordlists adaptées ;
    
- secrets dans fichiers, dépôts et configurations ;
    
- utilisation temporaire et protégée des identifiants autorisés.
    

### 9.7 Exploitation et post-exploitation

- recherche et sélection d’exploits ;
    
- vérification des préconditions ;
    
- adaptation contrôlée de PoC ;
    
- exploitation ;
    
- shells et sessions ;
    
- élévation ;
    
- tunnels et pivots ;
    
- mouvement latéral ;
    
- collecte minimale nécessaire ;
    
- preuve d’accès aux données ;
    
- arrêt dès que l’impact autorisé est suffisamment démontré.
    

### 9.8 Rapport, remédiation et retest

- classification CWE, OWASP et MITRE ATT&CK ;
    
- score technique et criticité métier ;
    
- actifs et rôles affectés ;
    
- recommandations concrètes ;
    
- validation des corrections ;
    
- comparaison avant/après ;
    
- conservation de l’historique du constat.
    

---

## 10. Outils, packs et extensibilité

Argos orchestre prioritairement les meilleurs outils existants. Il ne les  
réécrit que lorsqu’un manque ou un avantage mesurable le justifie.

|   |   |
|---|---|
|Domaine|Socle d’outils représentatif|
|OSINT et recon|RDAP/Whois, Amass, Subfinder, theHarvester, dnsx, httpx|
|Réseau|Nmap, Naabu ou Masscan, Netcat, Socat|
|Web/API|Katana, ffuf, Gobuster ou Feroxbuster, Nuclei, Nikto, sqlmap, curl, jq|
|Proxy et analyse|OWASP ZAP, mitmproxy, Burp Suite selon licence|
|Audit de code|Semgrep, Gitleaks, OSV-Scanner ou Trivy, analyseurs spécifiques aux langages|
|Mots de passe|Hydra, Ncrack, Hashcat, John the Ripper|
|Exploitation|Metasploit, Searchsploit, PoC contrôlés|
|Linux|PEASS-ng et outils spécialisés|
|Windows/AD|Impacket, NetExec, BloodHound, SharpHound, Responder, Evil-WinRM, enum4linux-ng, smbclient|
|Pivot|tunnels, proxies et routage contrôlé|
|Preuves|collecteurs Argos, logs, captures, hashes et horodatage|

La liste exacte, les versions, les licences et les alternatives seront définies  
dans `11_CATALOGUE_OUTILS_PLAYBOOKS_ET_SDK.md`.

Chaque capacité du registre déclare :

- identifiant et version ;
    
- objectif ;
    
- préconditions ;
    
- outils et agents compatibles ;
    
- entrées et sorties ;
    
- classe d’action ;
    
- risques et limites ;
    
- format de preuve ;
    
- validation indépendante attendue ;
    
- procédure de nettoyage ;
    
- benchmarks ;
    
- statut de maturité.
    

Les utilisateurs peuvent ajouter :

- outils ;
    
- scripts ;
    
- runners ;
    
- wordlists ;
    
- playbooks ;
    
- modèles ;
    
- méthodologies ;
    
- formats de rapport ;
    
- règles de validation.
    

Un ajout n’est utilisable professionnellement qu’après validation de sa  
provenance, de ses permissions, de ses résultats et de son comportement en  
benchmark.

---

## 11. Intelligence interne

Argos comprend au minimum :

- orchestrateur de mission ;
    
- agents spécialisés ;
    
- Model Gateway multi-fournisseurs et modèles locaux ;
    
- Scope Compiler ;
    
- Scope Guard ;
    
- Policy Engine déterministe ;
    
- planificateur ;
    
- registre de capacités ;
    
- Tool Executor ;
    
- runners isolés ;
    
- modèle vivant de la cible ;
    
- Cyber Graph ;
    
- matrice de couverture ;
    
- moteur d’hypothèses ;
    
- validateurs contradictoires ;
    
- Evidence Ledger ;
    
- registre des modifications ;
    
- moteur de rapport ;
    
- moteur de nettoyage et de retest ;
    
- mémoire persistante ;
    
- base de connaissances local-first ;
    
- journal d’audit.
    

### 11.1 Scope Compiler

Le Scope Compiler transforme le mandat, le programme ou la politique  
d’évaluation en règles techniques versionnées :

- actifs autorisés et exclus ;
    
- résolutions DNS et relations autorisées ;
    
- identités et rôles ;
    
- horaires ;
    
- classes d’action ;
    
- techniques interdites ;
    
- limites de débit, volume, durée et parallélisme ;
    
- autonomie et validations ;
    
- destinations de sortie ;
    
- conditions d’arrêt ;
    
- obligations de nettoyage.
    

Le résultat est lisible par l’utilisateur et exécutable par le Scope Guard.

### 11.2 Modèle vivant de la cible

Argos maintient les actifs, services, routes, identités, relations, constats,  
preuves et hypothèses dans un modèle versionné.

La couverture est suivie selon une matrice du type :

> actif × route ou service × rôle ou identité × état × paramètre × catégorie  
> de test

Cette matrice distingue ce qui a été :

- découvert ;
    
- planifié ;
    
- testé ;
    
- validé ;
    
- écarté ;
    
- bloqué par le scope ;
    
- non testé ;
    
- à retester.
    

### 11.3 Agents et validation contradictoire

Les agents proposent et exécutent des tâches spécialisées, mais les décisions  
critiques ne reposent pas sur une seule sortie de modèle.

Une vulnérabilité confirmée exige une reproduction indépendante ou une  
validation contradictoire utilisant, selon le cas :

- une autre méthode ;
    
- un autre outil ;
    
- un autre contexte d’exécution ;
    
- un validateur spécialisé ;
    
- une revue humaine.
    

---

## 12. Mémoire et connaissances

La mémoire appartient à Argos et reste indépendante d’un fournisseur de modèle.

Elle distingue :

- mémoire globale validée ;
    
- mémoire de projet ;
    
- mémoire de mission ;
    
- mémoire d’exécution ;
    
- archives brutes ;
    
- preuves ;
    
- connaissances candidates ;
    
- connaissances dépréciées.
    

Les données d’une mission client ne sont jamais promues dans une mémoire  
globale sans nettoyage, anonymisation et consentement explicite.

### 12.1 Référentiel local-first

Le socle local contient notamment :

- CISA KEV ;
    
- EPSS ;
    
- CVE/NVD rencontrées ou nécessaires ;
    
- MITRE ATT&CK ;
    
- CWE et CAPEC ;
    
- OWASP Top 10, API Security Top 10, WSTG, ASVS et Cheat Sheets ;
    
- documentation officielle des outils ;
    
- connaissances validées issues d’environnements autorisés.
    

Argos ne copie pas tout Internet. Il utilise :

1. un socle local sélectif ;
    
2. un cache progressif ;
    
3. des recherches officielles ciblées lorsque les données locales sont absentes  
    ou périmées.
    

### 12.2 Knowledge Sync

Knowledge Sync est un service déterministe sans LLM pour les mises à jour  
courantes. Il :

- récupère les deltas ;
    
- valide formats et métadonnées ;
    
- conserve la provenance et la fraîcheur ;
    
- normalise ;
    
- réindexe seulement les changements ;
    
- produit un rapport de synchronisation.
    

L’agent OSINT utilise le référentiel et peut demander un rafraîchissement ciblé.  
Il ne maintient pas seul la base et ne scrape pas silencieusement tout Internet.

### 12.3 Protection de la mémoire

Chaque élément important conserve :

- source ;
    
- date ;
    
- mission d’origine ;
    
- niveau de confiance ;
    
- statut de validation ;
    
- durée de validité ;
    
- droits de réutilisation.
    

Les contenus issus d’une cible ne deviennent jamais des instructions système.  
Les promotions de mémoire sont contrôlées, versionnées et réversibles.

---

## 13. Constats, preuves et retest

### 13.1 Cycle de vie d’un constat

Un constat passe par :

1. observation ;
    
2. hypothèse ;
    
3. tentative contrôlée ;
    
4. reproduction indépendante ;
    
5. contradiction et recherche de faux positif ;
    
6. preuve minimale ;
    
7. évaluation de l’impact ;
    
8. confirmation ;
    
9. rapport ;
    
10. correction ;
    
11. retest ;
    
12. clôture ou réouverture.
    

### 13.2 Evidence Ledger

L’Evidence Ledger relie :

- action ;
    
- outil et version ;
    
- commande ou paramètres ;
    
- cible ;
    
- opérateur ou agent ;
    
- date et heure ;
    
- requête et réponse utiles ;
    
- captures et artefacts ;
    
- hashes ;
    
- chaîne de vulnérabilités ;
    
- constat ;
    
- décision de validation ;
    
- niveau de confidentialité.
    

La preuve brute est conservée. Les rapports référencent les preuves sans les  
dupliquer ni les altérer.

### 13.3 Registre des modifications

Toute modification de cible produite par Argos est enregistrée avec :

- justification ;
    
- actif ;
    
- état avant ;
    
- action ;
    
- état attendu après ;
    
- méthode de rollback ;
    
- résultat du nettoyage ;
    
- vérification finale ;
    
- anomalie éventuelle.
    

---

## 14. Autorisation et sécurité

### 14.1 Application déterministe et fermée par défaut

Dans toute mission professionnelle ou de bug bounty, les limites suivantes sont  
appliquées par un contrôle déterministe indépendant des agents et des modèles :

- le mandat ou le règlement ;
    
- les actifs inclus et exclus ;
    
- la fenêtre autorisée ;
    
- les plafonds de débit, volume et parallélisme ;
    
- les techniques interdites ;
    
- les limites d’accès ou d’exfiltration ;
    
- les destinations réseau autorisées ;
    
- les conditions d’arrêt.
    

Une expérience Experte, un agent, un modèle ou une autonomie élevée ne peut pas  
désactiver ces limites. Si une cible, une règle ou une autorisation ne peut pas  
être résolue sans ambiguïté, l’action est refusée et la mission est suspendue si  
nécessaire.

Cette exigence est un objectif de sécurité vérifié en continu, pas l’affirmation  
qu’Argos ne pourrait jamais contenir de défaut.

### 14.2 Classes d’action

- **A0 — Lecture et analyse :** données déjà disponibles.
    
- **A1 — Interaction active faible :** probing, crawling, énumération  
    non destructive.
    
- **A2 — Exploitation contrôlée :** exploitation, authentification, upload,  
    shell ou modification temporaire.
    
- **A3 — Post-exploitation sensible :** élévation, pivot, mouvement latéral,  
    accès aux données.
    
- **A4 — Impact élevé :** persistance, perturbation, destruction, résilience ou  
    collecte importante.
    

Dans un environnement contrôlé appartenant à l’utilisateur, une politique peut  
préautoriser toutes les classes.

Dans une mission professionnelle, A4 doit être explicitement décrit par  
objectif, actif, limite et rollback. Il n’est jamais implicitement accordé par  
une option générale « tout autoriser ».

Dans un bug bounty, les règles du programme priment et A4 est interdit sauf  
autorisation écrite explicite.

### 14.3 Exposition d’Argos

- **E0 — Faible :** données locales connues et environnements maîtrisés.
    
- **E1 — Standard :** cible autorisée dont le contenu n’est pas maîtrisé.
    
- **E2 — Renforcée :** artefact inconnu à exécuter, suspicion de compromission  
    ou tentative visant Argos.
    

Les classes A0 à A4 mesurent l’impact sur la cible. Les niveaux E0 à E2  
mesurent le risque pour Argos. Les deux axes restent séparés.

### 14.4 Socle toujours actif

- control plane séparé des runners ;
    
- permissions minimales ;
    
- réseau limité au scope ;
    
- coffre de secrets ;
    
- actions structurées ;
    
- limites de ressources ;
    
- journal d’audit ;
    
- kill switch ;
    
- registre des modifications ;
    
- nettoyage ;
    
- isolation des clients et missions ;
    
- chiffrement en transit et au repos ;
    
- contrôle des transmissions vers les modèles externes.
    

### 14.5 Sécurité agentique

Argos doit résister notamment à :

- prompt injection indirecte ;
    
- détournement d’agent ;
    
- empoisonnement de mémoire ;
    
- résultat d’outil falsifié ;
    
- confusion entre donnée observée et instruction ;
    
- exfiltration par un outil ou un modèle ;
    
- extension malveillante ;
    
- escalade de permissions ;
    
- sortie du scope par redirection, DNS ou pivot.
    

Les politiques critiques sont déterministes. Argos ne peut pas modifier  
silencieusement son Scope Guard, ses règles critiques ou son code de production.

### 14.6 Intégrité des outils

Dès la V0 interne, chaque outil exécuté possède :

- une provenance connue ;
    
- une version épinglée ;
    
- un hash ou une signature vérifiable ;
    
- une licence enregistrée ;
    
- un manifeste de permissions ;
    
- une procédure de mise à jour et de rollback.
    

Un SBOM complet des composants distribués est obligatoire avant le pilote  
professionnel.

---

## 15. Architecture et données

### 15.1 Principes

- local et mono-utilisateur d’abord ;
    
- déploiement privé possible ;
    
- indépendance des modèles ;
    
- contrats structurés entre agents et outils ;
    
- séparation control plane / data plane ;
    
- runners remplaçables ;
    
- composants extensibles ;
    
- événements et états persistants ;
    
- reprise après interruption ;
    
- aucune dépendance obligatoire à Argos Arena.
    

### 15.2 Données et secrets

Argos distingue :

- données publiques ;
    
- connaissances personnelles ;
    
- données d’évaluation ;
    
- données de mission ;
    
- secrets ;
    
- preuves ;
    
- données exportables vers un modèle externe ;
    
- données strictement locales.
    

Principes :

- minimisation ;
    
- chiffrement ;
    
- coffre de secrets ;
    
- références temporaires plutôt que secrets dans les prompts ;
    
- séparation des missions ;
    
- rétention configurable ;
    
- suppression vérifiable ;
    
- redaction ;
    
- provenance ;
    
- intégrité ;
    
- journalisation sans fuite.
    

### 15.3 Scalabilité

La V0 peut fonctionner sur une seule machine. Les contrats et le modèle de  
données doivent cependant permettre :

- plusieurs runners ;
    
- files de tâches ;
    
- priorités et quotas ;
    
- exécution distribuée ;
    
- stockage croissant des preuves ;
    
- plusieurs utilisateurs et organisations ultérieurement.
    

---

## 16. Évaluation et amélioration

### 16.1 Interface de benchmark

Argos expose une interface standard :

> scénario + scope + budget + outils → actions + preuves + résultat + coût

Un évaluateur indépendant détermine ensuite le succès.

L’interface doit pouvoir être utilisée par :

- Argos Arena ;
    
- BountyBench ;
    
- AutoPenBench ;
    
- CyberGym ;
    
- Cybench ;
    
- des environnements internes ;
    
- d’autres benchmarks autorisés.
    

### 16.2 Métriques

- taux de réussite ;
    
- couverture ;
    
- vulnérabilités uniques confirmées ;
    
- faux positifs et faux négatifs ;
    
- chaînes d’attaque réussies ;
    
- temps total ;
    
- temps humain ;
    
- coût IA et infrastructure ;
    
- interventions humaines ;
    
- reproductibilité ;
    
- qualité des preuves ;
    
- qualité du rapport ;
    
- respect du scope ;
    
- effets secondaires ;
    
- réussite du nettoyage ;
    
- réussite du retest ;
    
- absence de régression.
    

### 16.3 Amélioration

Une amélioration suit :

1. observation d’un échec ou d’une opportunité ;
    
2. proposition ;
    
3. test isolé ;
    
4. comparaison avec la référence ;
    
5. validation ;
    
6. promotion versionnée ;
    
7. surveillance ;
    
8. rollback possible.
    

Les données client ne servent pas à l’entraînement ou à l’amélioration globale  
sans consentement explicite et traitement adapté.

---

## 17. Trajectoire de maturité

### 17.1 V0 interne

Objectif : démontrer un noyau offensif de bout en bout, local, mono-utilisateur  
et mesurable, sans prétendre couvrir exhaustivement chaque domaine.

La V0 conserve obligatoirement les fondations qui différencient Argos d’un  
assemblage de scanners :

- mission, autorisation, Scope Compiler et Scope Guard ;
    
- politique déterministe, classes A0 à A4 et expositions E0 à E2 ;
    
- runners isolés, journal d’audit, pause et kill switch ;
    
- modèle vivant minimal de la cible et matrice de couverture minimale ;
    
- Evidence Ledger et validation indépendante ;
    
- registre des modifications, nettoyage, rollback et retest ;
    
- rapport professionnel et résultats reproductibles.
    

Elle doit démontrer trois chaînes verticales obligatoires, volontairement  
étroites :

1. **Web/API** : cartographie, tests authentifiés simples, détection et validation  
   d’au moins une vulnérabilité représentative, preuve, rapport et retest. Une  
   analyse de code assistée limitée recherche secrets, dépendances et  
   motifs SAST, puis relie le constat à une validation dynamique autorisée.
2. **Réseau/Linux** : découverte, énumération, accès initial contrôlé, une  
   élévation locale représentative, preuve, nettoyage et retest.
3. **Windows/Active Directory** : énumération d’un petit domaine contrôlé,  
   détection d’une faiblesse, puis une chaîne représentative d’élévation ou de  
   mouvement latéral avec preuve minimale, nettoyage et retest.

Les simplifications suivantes s’appliquent :

- les expériences Guidée et Experte partagent une interface et un moteur ;  
    l’expérience Experte révèle les paramètres avancés ;
    
- Copilote et Supervisée sont utilisables sur les trois chaînes ;
    
- Autonome dans le scope est limité aux environnements contrôlés, isolés et  
    préautorisés pendant toute la V0 ;
    
- l’OSINT couvre uniquement la reconnaissance technique nécessaire aux scénarios ;
    
- le bug bounty couvre l’import des règles, la compilation du scope, l’exécution  
    supervisée de la chaîne Web/API et la préparation d’un rapport ; la validation  
    et la soumission finales restent humaines ;
    
- l’interface de benchmark est générique et validée sur les trois scénarios  
    locaux, sans imposer de connecteur externe ;
    
- le référentiel est local, minimal et mis à jour manuellement ou par une  
    synchronisation contrôlée ;
    
- une passerelle de modèles indépendante du fournisseur est prévue, sans routage  
    multi-modèles avancé ;
    
- le catalogue d’outils est réduit, épinglé et limité aux besoins des trois  
    scénarios.
    

La V0 est réalisée dans l’ordre suivant :

1. **V0-I1 — Noyau sécurisé** : mission, scope, politique, runners, journal,  
   Evidence Ledger, pause et kill switch.
2. **V0-I2 — Web/API** : première chaîne complète et audit de code limité.
3. **V0-I3 — Réseau/Linux** : deuxième chaîne complète.
4. **V0-I4 — Windows/Active Directory** : troisième chaîne représentative dans  
   un laboratoire contrôlé.
5. **V0-I5 — Qualification** : expériences Guidée et Experte, rapports,  
   benchmark, nettoyage, retest et critères chiffrés.

Chaque incrément doit être fonctionnel, vérifiable et accepté avant le suivant.  
Les scénarios exacts, preuves et seuils seront fixés dans  
`01_SCOPE_V0_ARGOS.md`.

### 17.2 Pilote professionnel

Objectif : exécuter des missions autorisées à faible risque avec supervision  
humaine forte.

Exigences supplémentaires :

- qualification professionnelle des trois chaînes de la V0 sur des scénarios plus  
    variés ;
    
- approfondissement ciblé de Windows/Active Directory sans prétendre à une  
    couverture exhaustive ;
    
- tests Web/API authentifiés multi-rôles ;
    
- validation des parcours black, grey et white box dans les limites annoncées ;
    
- gestion robuste des changements de règlement ;
    
- SBOM complet ;
    
- isolation et sauvegardes renforcées ;
    
- qualité de rapport validée par des professionnels ;
    
- procédures d’incident et de reprise ;
    
- conformité et contrats prêts ;
    
- zéro violation de scope sur la campagne de qualification.
    

### 17.3 MVP commercial

Objectif : proposer Argos à des utilisateurs externes dans un cadre maîtrisé.

Exigences supplémentaires :

- multi-utilisateur et multi-client ;
    
- RBAC ;
    
- séparation forte des tenants ;
    
- administration ;
    
- déploiement et mises à jour maîtrisés ;
    
- observabilité ;
    
- support ;
    
- conformité ;
    
- gestion des licences ;
    
- onboarding Guidé ;
    
- pilotes clients réussis.
    

### 17.4 V1

Objectif : élargir la profondeur et la continuité opérationnelle.

Capacités candidates :

- couverture Web/API avancée, notamment GraphQL, WebSocket et logique métier  
    complexe ;
    
- couverture réseau, Linux et Active Directory plus profonde, incluant des  
    chaînes multi-étapes et des environnements plus grands ;
    
- audit de code multi-langage approfondi, SAST, SCA, Infrastructure as Code,  
    CI/CD, correctifs assistés et tests de non-régression ;
    
- OSINT étendu aux personnes, organisations et fuites publiques ;
    
- Knowledge Sync complet ;
    
- SDK d’outils, playbooks et packs personnalisés ;
    
- routage multi-modèles avancé ;
    
- connecteurs vers des benchmarks externes autorisés ;
    
- cloud, conteneurs et Kubernetes ;
    
- mobile ;
    
- wireless et IoT ;
    
- évaluation offensive continue ;
    
- packs spécialisés.
    

Le SOC, le forensic, l’analyse de malware, le phishing et l’ingénierie sociale  
ne font pas partie de la feuille de route actuelle. Ils ne seront ajoutés  
qu’après une décision produit distincte démontrant qu’ils ne diluent pas  
l’excellence offensive d’Argos.

---

## 18. Hors périmètre de la V0 interne

- SaaS public ;
    
- multi-tenant commercial ;
    
- facturation ;
    
- support avec SLA ;
    
- accès autonome à TryHackMe ou Hack The Box ;
    
- soumission automatique de rapports bug bounty ;
    
- autonomie complète sur des cibles professionnelles réelles ;
    
- couverture Web/API exhaustive, logique métier complexe, GraphQL et WebSocket  
    avancés ;
    
- grands environnements Active Directory, chaînes multi-étapes et mouvements  
    latéraux complexes ;
    
- audit de code multi-langage approfondi, SCA et IaC complets, intégration CI/CD  
    et génération automatique de correctifs ;
    
- OSINT approfondi sur les personnes, organisations et fuites ;
    
- Knowledge Sync complet et collecte massive de sources ;
    
- routage multi-modèles avancé, SDK public et packs personnalisés ;
    
- connecteurs complets vers les benchmarks externes ;
    
- phishing et ingénierie sociale ;
    
- actions destructrices non explicitement autorisées ;
    
- SOC, SIEM et Blue Team ;
    
- réponse à incident et forensic ;
    
- analyse de malware ;
    
- reverse engineering et exploit development avancés ;
    
- cloud, Kubernetes et mobile complets ;
    
- couverture exhaustive de toutes les vulnérabilités ;
    
- auto-modification non contrôlée du code ou des politiques critiques ;
    
- fine-tuning requis pour fonctionner.
    

---

## 19. Direction de l’interface

Argos s’ouvre sur un dashboard opérationnel.

Navigation cible :

- Dashboard ;
    
- Missions ;
    
- Surface d’attaque ;
    
- OSINT ;
    
- Web/API ;
    
- Infrastructure ;
    
- Identités/AD ;
    
- Constats ;
    
- Evidence ;
    
- Rapports ;
    
- Knowledge ;
    
- Outils et playbooks ;
    
- Agents ;
    
- Paramètres.
    

Parcours de création :

> Autorisation → Cibles → Objectifs → Techniques → Outils → Intensité →  
> Autonomie → Plan → Validation → Exécution

En expérience Guidée, ces étapes sont formulées en questions métier et Argos  
propose les choix. En expérience Experte, tous les paramètres restent  
accessibles.

L’interface d’exécution affiche toujours :

- scope verrouillé ;
    
- plan approuvé ;
    
- cible exacte ;
    
- action en cours ;
    
- risque ;
    
- progression ;
    
- preuves ;
    
- modifications ;
    
- approbations ;
    
- pause ;
    
- kill switch.
    

---

## 20. Critères généraux de réussite

Argos progresse uniquement si les résultats sont mesurés.

La V0 interne ne sera pas considérée comme terminée tant que :

- les trois scénarios Web/API, réseau/Linux et Windows/Active Directory ne  
    réussissent pas de bout en bout ;
    
- aucune action ne dépasse le scope pendant les tests de qualification ;
    
- les vulnérabilités confirmées disposent de preuves reproductibles ;
    
- la validation indépendante réduit effectivement les faux positifs ;
    
- la matrice de couverture reflète ce qui a réellement été testé ;
    
- le nettoyage et le retest sont démontrés ;
    
- les rapports sont exploitables ;
    
- l’expérience Guidée permet à un non-spécialiste de terminer une mission  
    contrôlée ;
    
- l’expérience Experte permet de reprendre la main sans contourner la sécurité ;
    
- l’audit de code limité relie ses constats retenus à une preuve dynamique  
    autorisée ou les marque explicitement comme non confirmés ;
    
- le niveau Autonome dans le scope reste techniquement limité aux environnements  
    contrôlés et préautorisés ;
    
- les outils sont versionnés, traçables et remplaçables ;
    
- les résultats sont reproductibles avec une version donnée d’Argos.
    

Les scénarios et seuils chiffrés seront fixés dans  
`01_SCOPE_V0_ARGOS.md` et `12_PROTOCOLE_EVALUATION_ET_BENCHMARK.md`.

---

## 21. Plan documentaire

### Gouvernance

- `00_PRODUCT_BRIEF_ET_PLAN_GLOBAL_ARGOS.md` — vision et trajectoire ;
    
- `CANONICAL_MANIFEST_ARGOS.md` — documents canoniques, versions et  
    dépendances ;
    
- `PROJECT_STATUS_ARGOS.md` — état courant, décisions récentes et prochaine  
    étape ;
    
- `AGENTS.md` — instructions du dépôt, créé après les spécifications  
    structurantes et avant le développement.
    

### Produit

1. `01_SCOPE_V0_ARGOS.md`
    
2. `02_PARCOURS_MISSION_ET_UTILISATEURS.md`
    

### Autorisation, sécurité et conformité

3. `03_AUTORISATION_SCOPE_ET_RULES_OF_ENGAGEMENT.md`
    
4. `04_THREAT_MODEL_ET_SECURITE_ARGOS.md`
    
5. `05_CONFORMITE_DONNEES_ET_CONTRATS.md`
    

### Architecture et IA

6. `06_ARCHITECTURE_TECHNIQUE.md`
    
7. `07_SYSTEME_MULTI_AGENTS_ET_WORKFLOWS.md`
    
8. `08_MODELE_DE_DONNEES_ET_ATTACK_SURFACE_GRAPH.md`
    
9. `09_CONTRATS_API_ET_SCHEMAS.md`
    
10. `10_STRATEGIE_MODELES_IA.md`
    
11. `11_CATALOGUE_OUTILS_PLAYBOOKS_ET_SDK.md`
    

### Qualité et réalisation

12. `12_PROTOCOLE_EVALUATION_ET_BENCHMARK.md`
    
13. `13_BACKLOG_EPICS_ET_STORIES.md`
    
14. `14_PLAN_DE_TEST_SECURITE_ET_QA.md`
    
15. `15_PLAN_DE_DEPLOIEMENT_ET_OPERATIONS.md`
    

### Commercialisation différée

16. `16_OFFRE_COMMERCIALE_ET_PRICING.md`
    
17. `17_PLAN_PILOTES_CLIENTS.md`
    
18. `18_SUPPORT_SLA_ET_GESTION_INCIDENTS.md`
    
19. `19_ROADMAP_MODULES_ARGOS.md`
    

`GUIDE_TRAVAIL_ARGOS_AVEC_CHATGPT.md` est retiré du corpus actif et absent du  
dépôt. Il n’a aucune autorité.

---

## 22. Décisions fondatrices figées

- Argos est une plateforme professionnelle de cybersécurité offensive.
    
- Argos et Argos Arena sont indépendants.
    
- Argos utilise un moteur unique.
    
- Les deux expériences sont Guidée et Experte.
    
- Elles utilisent le même moteur et le même registre de capacités ; l’expérience  
    Guidée applique davantage de protections et masque les réglages avancés.
    
- Learn, Lab et Operator ne sont pas des modes.
    
- L’apprentissage est une option pédagogique.
    
- Le laboratoire est un type d’environnement autorisé.
    
- Les autonomies sont Copilote, Supervisée et Autonome dans le scope.
    
- Les cadres sont pentest mandaté, bug bounty/VDP et évaluation contrôlée.
    
- Le bug bounty est supervisé avant maturité commerciale.
    
- La soumission d’un rapport bug bounty reste humaine dans la V0 et le pilote.
    
- Argos ne dépend pas de plateformes interdisant les bots ou agents IA.
    
- Black box, grey box et white box sont pris en charge.
    
- La V0 interne est réalisée en cinq incréments successifs et vérifiables.
    
- Les chaînes Web/API, réseau/Linux et Windows/Active Directory sont toutes trois  
    obligatoires dans la V0, avec une profondeur volontairement limitée.
    
- L’audit de code limité appartient à la chaîne Web/API de la V0 ; l’AppSec  
    approfondi est reporté à la V1.
    
- Dans la V0, Autonome dans le scope est réservé aux environnements contrôlés et  
    préautorisés.
    
- Le bug bounty de la V0 reste supervisé, sans soumission automatique.
    
- Les tests authentifiés multi-rôles font partie de la cible professionnelle.
    
- Le mandat et le scope sont compilés en règles techniques.
    
- Le Scope Guard et les plafonds ne sont jamais désactivés en mission  
    professionnelle.
    
- A4 exige une autorisation spécifique en mission professionnelle.
    
- Le modèle vivant de la cible et la matrice de couverture sont des fondations.
    
- L’Evidence Ledger est une fondation.
    
- Une vulnérabilité confirmée exige une validation indépendante.
    
- Le registre des modifications, le nettoyage et le retest font partie de la  
    mission.
    
- Argos orchestre les outils professionnels existants avant de les réécrire.
    
- Les outils sont épinglés, vérifiés et traçables dès la V0.
    
- Argos protège sa mémoire et ses agents contre les contenus hostiles.
    
- La connaissance est local-first, sélective et complétée par recherche ciblée.
    
- Knowledge Sync est déterministe et distinct de l’agent OSINT.
    
- La mémoire et les preuves appartiennent à Argos, pas au fournisseur de modèle.
    
- Les données client ne servent pas à l’entraînement sans consentement explicite.
    
- La V0 interne, le pilote professionnel, le MVP commercial et la V1 sont des  
    jalons distincts.
    
- La performance est évaluée par des scénarios et métriques reproductibles.
    
- Le développement commence localement avant l’industrialisation.
    

---

## 23. Décisions à préciser

Les sujets suivants ne remettent pas en cause la vision :

- scénarios exacts et seuils de la V0 interne ;
    
- vulnérabilités représentatives et profondeur exacte de chacune des trois  
    chaînes obligatoires ;
    
- langages, règles et outils exacts de l’audit de code limité ;
    
- stack frontend, backend et orchestrateur ;
    
- base du Cyber Graph ;
    
- stockage des événements et preuves ;
    
- moteur de recherche vectorielle ;
    
- modèles et fournisseurs principaux ;
    
- versions exactes des outils ;
    
- limites de ressources ;
    
- formats et durée de conservation ;
    
- architecture de déploiement ;
    
- disponibilité juridique et commerciale du nom Argos ;
    
- seuils d’entrée en pilote professionnel.
    

---

## 24. Étape suivante

Créer `01_SCOPE_V0_ARGOS.md` afin de transformer cette vision en exigences  
vérifiables :

- cinq incréments ordonnés ;
    
- trois scénarios verticaux obligatoires : Web/API, réseau/Linux et  
    Windows/Active Directory ;
    
- capacités obligatoires et différées ;
    
- entrées et sorties ;
    
- parcours Guidé et Expert ;
    
- autonomies ;
    
- classes d’action ;
    
- outils minimaux ;
    
- audit de code limité et frontière avec l’AppSec V1 ;
    
- exigences de sécurité ;
    
- benchmarks ;
    
- critères d’acceptation chiffrés ;
    
- définition de terminé de la V0 interne.
