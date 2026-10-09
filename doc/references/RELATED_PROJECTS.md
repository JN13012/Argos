# Projets proches d'Argos

**Consultation initiale :** 7 octobre 2026. **Mise à jour ciblée :** 9 octobre 2026
(GrepLeaks et état des réalisations Argos). Les observations sur les autres
projets conservent leur date initiale et n'ont pas été revalidées lors de cette
mise à jour. Cette revue décrit les positionnements et
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
| [GrepLeaks](https://github.com/grepleaks/grepleaks) | Environnement de pentest assisté par IA dans le terminal, agent conversationnel, catalogues de skills et d'outils, runner Linux/Docker jetable | Séparation méthode/outillage, catalogue de capacités, installation à la demande, état persistant hors runner et actions observables | Source available : Grepleaks Source Available License 1.0 pour les contributions originales ; licences propres pour OpenCode et les composants tiers |

RedClaude et Claude-Red portent des noms proches mais sont des projets
différents. Pour RedClaude, les informations du README sont consultables via la
source Web, mais la disponibilité actuelle et la licence n'ont pas été
confirmées par l'API GitHub ; en faire une référence documentaire provisoire.
Pour CAI, le README et l'API GitHub indiquent l'archivage. Le README annonce
l'absence de nouvelles corrections et décrit des conditions de licence mixtes.

## GrepLeaks — référence de conception à approfondir

Sources primaires consultées le 9 octobre 2026 : [site officiel](https://grepleaks.com/),
[présentation](https://grepleaks.com/about), [documentation](https://grepleaks.com/docs),
[licences](https://grepleaks.com/docs/licensing) et
[dépôt GitHub](https://github.com/grepleaks/grepleaks). Cette lecture documentaire
ne constitue pas une installation, une évaluation de performance ou une
validation des contrôles annoncés.

### Positionnement et mécanismes décrits

- **Terminal et agent conversationnel :** le projet réunit conversation,
  sorties d'outils et catalogue dans une interface terminal. Sa présentation
  indique une construction sur un fork d'OpenCode et OpenTUI.
  [Présentation officielle](https://grepleaks.com/about).
- **Méthodes et outils distincts :** le [catalogue de skills](https://grepleaks.com/docs/skills)
  décrit des méthodes, des outils associés et les preuves à conserver. Le site
  annonce plus de 900 outils au catalogue et plus de 120 skills ; ce sont des
  chiffres annoncés, sans inventaire indépendant ni mesure de couverture ici.
  Un socle d'outils accompagne l'image, puis des outils compatibles peuvent être
  installés à la demande. Une entrée de catalogue ne signifie pas qu'un outil
  est installé ou validé. [Site officiel](https://grepleaks.com/),
  [README du projet](https://github.com/grepleaks/grepleaks).
- **Runner jetable et persistance conditionnelle :** l'environnement Linux
  basé sur Debian s'exécute dans Docker. Un dossier d'engagement hôte monté
  conserve rapports, scripts et preuves après destruction du conteneur ; sans
  ce montage, les fichiers d'engagement ne persistent pas. L'historique des
  conversations et les réglages disposent d'un stockage privé séparé ; les
  installations supplémentaires d'outils restent jetables.
  [README du projet](https://github.com/grepleaks/grepleaks).
- **Permissions et frontière avec l'hôte :** les configurations standard
  demandent des approbations pour l'exécution et l'écriture ; des configurations
  avancées peuvent changer cette politique. Les montages hôte sont explicites,
  mais le compagnon de commandes natives est activé par défaut. Ses demandes
  passent par le flux d'approbation de l'interface et l'exécution se déroule hors
  Docker. La documentation précise que ces contrôles applicatifs ne constituent
  pas un sandbox de l'hôte. Les demandes, permissions et sorties visibles sont
  des pistes d'observabilité, sans audit de leur exhaustivité dans cette revue.
  [Sécurité](https://grepleaks.com/docs/security),
  [accès aux fichiers hôte](https://grepleaks.com/docs/host-access),
  [compagnon hôte](https://grepleaks.com/docs/host-companion).

### Licence et provenance

GrepLeaks est **source available, pas OSI open source**. Les contributions
originales relèvent de la **Grepleaks Source Available License 1.0** ; son texte
restreint notamment la revente et l'accès payant au logiciel sans permission
séparée. [Présentation des licences](https://grepleaks.com/docs/licensing),
[texte de la licence](https://github.com/grepleaks/grepleaks/blob/main/LICENSE).

Le matériel hérité d'OpenCode conserve sa licence MIT. Les skills et autres
composants tiers conservent leurs notices et licences propres ; dans un fichier
mêlant contributions héritées et ajouts GrepLeaks, la provenance de chaque partie
doit être examinée. La disponibilité des sources n'autorise donc aucune
conclusion générale sur leur réutilisation dans Argos sans analyse fichier par
fichier, au commit exact envisagé.
[Notice du moteur](https://github.com/grepleaks/grepleaks/blob/main/engine/GREPLEAKS_LICENSE.md),
[notices tierces du projet](https://github.com/grepleaks/grepleaks/blob/main/THIRD_PARTY_NOTICES.md).

Argos utilise GrepLeaks uniquement comme référence de conception et de
recherche. Aucun code, skill ou asset GrepLeaks n'est repris ; aucune entrée
n'est ajoutée aux notices d'imports d'Argos.

### Pistes d'étude pour Argos

Les pistes suivantes sont notre appréciation, pas des décisions d'architecture
adoptées ni des capacités déjà implémentées dans Argos :

| Axe | Questions à étudier |
| --- | --- |
| Méthodes et registre | Séparer skill/méthode et outil concret ; examiner le routage situation → skill → outil et sa représentation dans un registre de capacités |
| Disponibilité et cycle de vie | Étudier l'installation à la demande plutôt qu'une image contenant tout, la vérification de disponibilité/version et le cycle sélection → installation → exécution → preuves → nettoyage |
| Persistance | Conserver preuves et état de mission hors du runner jetable ; étudier la reprise après recréation du runner et les conditions de restauration |
| Permissions | Examiner les permission/approval gates et distinguer exécution containerisée, montages de fichiers et accès explicite à l'hôte, en tenant compte des configurations par défaut |
| Observabilité | Examiner les traces des demandes, décisions, actions et résultats de l'agent et leurs liens avec les preuves |

**À approfondir :** réanalyser GrepLeaks lors de la conception de
`06_ARCHITECTURE_TECHNIQUE.md`, `07_SYSTEME_MULTI_AGENTS_ET_WORKFLOWS.md` et
`11_CATALOGUE_OUTILS_PLAYBOOKS_ET_SDK.md`. Ces documents restent planifiés et ne
sont pas créés dans cette mise à jour. Les choix d'Argos devront être évalués
selon ses propres exigences ; cette référence n'étend pas le scope V0 proposé.

## Repères commerciaux

| Produit | Périmètre présenté par l'éditeur | Intérêt pour la vision |
| --- | --- | --- |
| [XBOW](https://docs.xbow.com/console/get-started/introduction/) | Tests automatisés Web/API et résultats associés à des preuves | Lisibilité des résultats et traçabilité |
| [NoScope](https://www.noscope.com/) | Pentest IA avec supervision humaine, contrôles de scope et approbations | Parcours de revue et contrôle opérateur |
| [NodeZero](https://horizon3.ai/nodezero/) | Évaluations internes, externes, cloud et identités, avec vérification des corrections | Restitution du risque et suivi des corrections |
| [Pentera](https://pentera.io/pentera-platform/) | Validation d'exposition sur réseau interne, actifs externes et cloud | Priorisation, gestion des corrections et mesure dans le temps |

Ce sont des repères concurrentiels pour la vision produit. Cette revue ne leur
attribue aucune autorisation de réutilisation de code.

## Réalisations et références pour la suite

### Déjà implémenté

La CLI hors ligne proposée lors de la revue du 7 octobre est désormais
**Argos Core 0.1.0** : création/import de missions, validation des preuves,
revue humaine et rapport Markdown déterministe, avec fixtures, tests et CI.
Son périmètre est fixé dans le [premier livrable](../livrables/FIRST_DELIVERABLE.md).
Le [front React/TypeScript](../interface/FRONTEND.md) et
[Discovery V0](../livrables/DISCOVERY_V0.md) sont réalisés comme prototypes
séparés ; le front n'est raccordé à aucun des deux moteurs.

### Toujours utiles au prochain travail

La prochaine tranche Core proposée reste la **persistance et la reprise de
missions**, avec un contrat à définir. **Red Clippy et DefectDojo** restent utiles
pour le modèle de données, les preuves et le suivi des corrections ; **Strix et
Shannon** pour la lisibilité des rapports ; **PentestGPT** pour la discipline
d'évaluation. Ces références sont des pistes d'étude, sans reprise de code.

L'acceptation des entrées valides, le rejet des entrées invalides et la
reproductibilité de l'export disposent déjà de tests hors ligne. Les campagnes
comparatives et mesures de performance restent à définir ; les critères de
démo ne constituent pas des résultats de benchmark.

### À analyser plus tard

GrepLeaks sera réexaminé pour les futurs documents d'architecture, d'agents et
d'outillage cités ci-dessus. Les fonctions avancées des autres projets restent
des références pour ces lots futurs, sans adoption anticipée dans le noyau ni
validation du scope V0.

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
