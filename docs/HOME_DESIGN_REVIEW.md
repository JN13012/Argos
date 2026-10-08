# Revue de l’accueil Argos

L’accueil doit permettre de choisir la prochaine action et de reprendre un
dossier. Chaque information dispose d’un emplacement principal ; chaque bouton
ouvre un contenu ou effectue une action distincte.

## Organisation retenue

| Zone | Contenu et action |
| --- | --- |
| Bandeau | Logo et consigne courte, adaptée à l’état du dossier ; aucun compteur ni rappel de mission |
| Mission | Nom, identifiant, périmètre et état de revue, puis constats à examiner directement accessibles |
| Rapports et documents | Rapport disponible à droite, avec une seule action de téléchargement |
| Journal de logs | Événements de session récents, trois lignes maximum avant développement |
| Argos Chat | Champ de saisie sous les logs ; conversation et raccourcis ouverts à la demande |

La mission constitue le contenu principal. Son titre et son périmètre ne sont
plus répétés dans un bandeau, une carte de compteur et une seconde carte de
mission. Le nombre de constats à examiner figure seulement à côté de leur
liste. La sévérité est attachée à chaque constat ; une observation critique se
repère dans cette liste lorsqu’elle existe. Le front n’affiche pas de carte
« zéro constat critique » ni de score de sécurité global.

Les preuves et la progression de revue appartiennent au dossier, accessible par
« Ouvrir le dossier ». Cliquer sur un constat ouvre directement ce constat avec
ses preuves. « Voir toute la mission » réaffiche l’ensemble du dossier.
Le contexte de mission reste disponible dans la conversation lorsqu’elle est
ouverte, et les références de mission dans les événements du journal.

## Éléments retirés

- La rangée de compteurs « Missions à revoir », « Constats à revoir »,
  « Constats critiques » et « Preuves référencées ».
- Les rappels « Vos priorités » et « Mission à examiner » qui répétaient le
  même état ou ouvraient le même dossier.
- Le panneau de notifications alimenté uniquement par ces constats en attente.
- Le document JSON qui rouvrait la mission et les boutons de téléchargement
  dupliqués. Le rapport comporte une seule action dans la colonne de droite.
- Les résumés de mission produits automatiquement dans le chat et les lignes
  de logs générées uniquement pour annoncer les métadonnées déjà affichées.
- Les cartes Red Team, OSINT et Blue Team, déjà présentes dans la navigation.
- Les profils d’agents inexistants, les courbes sans mesure, les slogans et les
  mentions « Démo » dans le parcours courant.

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
reste visible ; une question, le bouton de conversation ou le raccourci de
l’en-tête ouvre les échanges. Le mode agrandi conserve le contexte et se réduit
avec Échap. Replier la conversation conserve les messages pendant la session.

## Évolution de l’accueil

La version React du 8 octobre 2026 conserve cette organisation. Les composants
de mission, de documents, de journal et de conversation sont séparés. Les
styles partagés emploient des variables de thème, avec des textes plus lisibles,
des espacements réguliers et une action de téléchargement clairement identifiée.
La logique de présentation et les contrôles de cohérence du rapport restent
indépendants de React ; le chargement passe par une source de données explicite.
Le mode agrandi du chat utilise un dialogue natif, conserve le brouillon et les
messages, maintient le focus au clavier et revient à son bouton d'ouverture.
Les détails de structure et de vérification sont dans
[frontend/README.md](../frontend/README.md).

Avec plusieurs missions, le bloc principal pourra devenir une liste de dossiers
à reprendre, chaque mission conservant une seule ligne de résumé. Responsable,
dernière activité et blocages ne seront ajoutés que lorsque les données les
exposeront. Ces champs ne sont pas inventés dans la version actuelle.
Le raccordement aux dossiers locaux d’Argos Core reste une tranche séparée.
