# Revue de l’accueil Argos

**Status: ARCHIVED / SUPERSEDED.**

Revue historique d'une étape frontend terminée. Le comportement actuel est documenté dans le [guide du front](../../interface/FRONTEND.md).

Le contenu ci-dessous est conservé pour mémoire. Ses anciens statuts, décisions
et prochaines étapes ne définissent plus le corpus actif.

À la demande du propriétaire, l'accueil reprend la présentation de « Front init »
(`8d4dccd`) : mascotte d'origine, couleurs sombres, bandeau de bienvenue,
indicateurs et chat à droite. Cette restauration conserve les composants React,
la consultation des preuves, la cohérence du rapport et les états de chargement.

## Organisation retenue

| Zone                  | Contenu et action                                                                       |
| --------------------- | --------------------------------------------------------------------------------------- |
| Bandeau               | Mascotte d'origine, bienvenue, heure locale, état de revue et point de situation        |
| Indicateurs           | Mission, revues en attente, actifs du périmètre, constats critiques et agents connectés |
| Mission               | Nom, identifiant, périmètre, progression de revue et constats directement accessibles   |
| Rapports et documents | Rapport et dossier dans le premier panneau, avec une seule action de téléchargement     |
| Agents                | Profils prévus explicitement non connectés, zéro agent connecté                         |
| Journal de logs       | Événements de session récents, trois lignes maximum avant développement                 |
| Argos Chat            | Conversation ouverte à droite sur ordinateur, sous la synthèse sur les petits écrans    |

Les compteurs sont calculés depuis le dossier chargé. Les graphiques des cartes
sont des décorations, sans série de mesures ni score de sécurité global. Les
notifications reprennent les constats en attente. Le titre de mission figure
dans son panneau et dans le contexte du chat ; la sévérité reste attachée à
chaque constat.

Les preuves et les décisions de revue appartiennent au dossier, accessible par
« Ouvrir le dossier ». Cliquer sur un constat ouvre directement ce constat avec
ses preuves. « Voir toute la mission » réaffiche l’ensemble du dossier.
Le contexte de mission reste disponible dans la conversation lorsqu’elle est
ouverte, et les références de mission dans les événements du journal.

## Limites de la présentation

Le panneau Agents décrit une présentation prévue, sans activité inventée.
La navigation Red Team, OSINT et Blue Team reste désactivée. Les événements du
journal correspondent aux interactions locales ; le message d'accueil du chat
est une introduction fixe. Le dossier JSON s'ouvre dans le dialogue de mission,
et seul le rapport correspondant peut être téléchargé.

Les sorties d’outils complètes, contenus de preuves, secrets et prompts internes
ne doivent pas occuper l’accueil. Les détails utiles à la revue appartiennent
au dossier.

## États et cohérence des données

Le dossier fictif `MIS-001`, « Audit de configuration interne », utilise
`intranet.example` comme actif d’exemple ; aucun système n’a été testé.
Les preuves viennent des fixtures originales et conservent leur provenance.
Le rapport est produit par Argos Core depuis le même dossier.

Les constats à examiner sont triés par sévérité. Une mission sans constat affiche
« Sans constat » ; toutes les décisions enregistrées donnent « Revue terminée »,
y compris si certains constats sont rejetés. Une décision humaine acceptée ne
constitue pas une confirmation technique de vulnérabilité.

L’accueil distingue le chargement, l’absence explicite de mission et les données
indisponibles ou incompatibles. Les actions de mission sont alors masquées ou
désactivées ; aucune donnée d’exemple ne remplace une donnée absente.
La navigation et l’aide restent accessibles lorsque le dossier est indisponible.
Le contrôle d’affichage ne vérifie pas les fichiers de preuve et ne remplace
pas la validation d’Argos Core. Une empreinte déclarée n’est pas une intégrité
vérifiée par ce front.

Le rapport embarqué est proposé uniquement si l’empreinte du dossier affiché
correspond à celle du dossier utilisé pour le produire. Une modification de
revue ou de contenu rend ce téléchargement indisponible jusqu’à ce qu’un
rapport correspondant soit fourni. Le front ne régénère pas les rapports.

## Journal et conversation

Le journal contient des événements réels de la session d’interface : chargement
du dossier, consultation de mission ou de constat et demande de téléchargement.
Il ne présente pas d’activité d’agents ou de moteur de pentest. Les horodatages
viennent du navigateur et sont affichés en Europe/Paris. Les événements restent
en mémoire, disparaissent au rechargement et sont limités à 100.
Trois événements filtrés sont visibles initialement, du plus récent au plus
ancien. Développer le journal affiche tous les résultats dans une zone défilante.

Le chat reste un assistant local à réponses prédéfinies, sans modèle connecté.
Cette limite est décrite dans l’aide et la documentation. Le champ de saisie
reste visible et la conversation est ouverte à l'arrivée. Le bouton de
conversation ou le raccourci de l'en-tête permet de la rouvrir après réduction.
Le mode agrandi conserve le contexte et se réduit
avec Échap. Replier la conversation conserve les messages pendant la session.

## Évolution de l’accueil

La restauration de l'accueil conserve la structure React du 8 octobre 2026. Les composants
de mission, de documents, de journal et de conversation sont séparés. Les
styles reprennent le thème de « Front init », adapté aux composants actuels.
La logique de présentation et les contrôles de cohérence du rapport restent
indépendants de React ; le chargement passe par une source de données explicite.
Le mode agrandi du chat utilise un dialogue natif, conserve le brouillon et les
messages, maintient le focus au clavier et revient à son bouton d'ouverture.
Les détails de structure et de vérification sont dans
[le guide du front](../../interface/FRONTEND.md).

Avec plusieurs missions, le bloc principal pourra devenir une liste de dossiers
à reprendre, chaque mission conservant une seule ligne de résumé. Responsable,
dernière activité et blocages ne seront ajoutés que lorsque les données les
exposeront. Ces champs ne sont pas inventés dans la version actuelle.
Le raccordement aux dossiers locaux d’Argos Core reste une tranche séparée.
