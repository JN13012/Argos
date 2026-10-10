# Accueil Argos

Dashboard React + TypeScript + Vite, inspiré des propositions visuelles du
propriétaire. L'accueil adapte la présentation de « Front init » (`8d4dccd`) :
logo wolf-kraken dans l'en-tête, cinq indicateurs et panneaux Documents,
Mission et Agents. La conversation est ouverte à droite sur ordinateur et le
journal de logs se trouve dessous. Les styles et les ressources sont locaux ;
aucune police distante ni CDN.

Le code reste dans `frontend/`. Sauf indication contraire, les chemins de source
et les commandes de ce guide sont relatifs à ce dossier ; les liens Markdown
pointent vers la documentation regroupée dans `doc/`.

## Lancer le front

Node.js **24 ou supérieur** et npm sont nécessaires. Depuis la racine du dépôt :

```bash
cd frontend
npm ci
npm run dev
```

Ouvrir **http://localhost:8000**. Le serveur écoute uniquement sur `127.0.0.1`.
Arrêter avec `Ctrl+C`. L'installation initiale récupère les dépendances npm.
Une fois les dépendances disponibles, le dashboard fonctionne localement sans
clé d'API ni accès à un service externe.

Pour consulter la version compilée :

```bash
npm run build
npm run preview
```

`dist/` est généré et ignoré par Git. L'ouverture directe de `index.html` avec
`file://` et l'ancien serveur Python pointant sur `frontend/` ne conviennent plus
au projet source. La compilation produit des ressources statiques utilisables
avec un serveur HTTP ; elle n'ajoute pas de serveur applicatif.

## Périmètre et comportement

Seul l'accueil est implémenté. Les autres espaces restent désactivés : Red Team,
OSINT, Blue Team, Preuves, Rapports, Agents et Paramètres. La création de mission
reste une fonctionnalité future.

- Recherche dans les constats et documents, insensible aux accents, accessible
  par `Ctrl+K` ou `Cmd+K` sur ordinateur.
- Ouverture du dossier complet ou d'un constat avec ses preuves et les décisions
  de revue. Les dialogues natifs gèrent le clavier, le focus et `Échap`.
- Les indicateurs et notifications utilisent les données du dossier affiché.
  Le panneau Agents présente des profils prévus, avec zéro agent connecté.
- Un seul téléchargement de rapport, proposé lorsque l'empreinte du dossier
  affiché correspond au dossier utilisé pour générer le rapport.
- Logs de consultation et de demande de téléchargement, horodatés en Europe/Paris.
  Trois événements visibles initialement, journal développable, filtres par type.
  Les 100 derniers événements restent en mémoire jusqu'au rechargement.
- Argos Chat à réponses prédéfinies : questions, raccourcis et messages en texte
  simple. La conversation conserve ses messages et son brouillon lorsqu'elle
  est repliée ou agrandie. Elle est limitée à 42 messages et 500 caractères par
  question. Aucun modèle IA ni moteur d'analyse n'est connecté.
- États de chargement, absence explicite de mission, données incompatibles et
  erreur de lecture distincts. Une erreur ne provoque aucun remplacement par
  des données fictives ; la navigation et l'aide restent accessibles.

## Données et limites

`src/fixtures/workspace.json` décrit le cas fictif `MIS-001`, « Audit de
configuration interne », avec `intranet.example` comme actif d'exemple.
Il dérive des fixtures originales `examples/offline/` et conserve les chemins,
empreintes et provenance des deux preuves synthétiques. Aucun système n'a été testé.

`assets/mission-report.md` est produit par Argos Core à partir de ce même dossier.
Le téléchargement ne génère pas de rapport. La comparaison SHA-256 porte sur
le JSON canonique du dossier, pas sur les fichiers de preuve. Si le dossier est
modifié ou Web Crypto indisponible, le rapport précédent n'est pas proposé.

Le front ne lit pas de fichiers de preuve, n'exécute pas d'outil et n'est pas
connecté à Argos Core. Une revue humaine ne confirme pas techniquement une
vulnérabilité. Le contrôle de présentation ne remplace pas la validation du
noyau Python. Le contrat `schema_version: 1` reste celui du livrable hors ligne.

## Organisation du code

```text
src/
  app/                 Assemblage de l'application et aide
  components/          Boutons, badges, icônes, logo et dialogue partagés
  layout/              En-tête, recherche, navigation et adaptation mobile
  features/
    workspace/         Contrat typé, contrôles, résumé, source et empreinte
    home/              Composition de l'accueil, mission et rapport
    mission/           Consultation du dossier et des constats
    activity/          Événements de session et journal filtrable
    chat/              Conversation et réponses locales
  fixtures/            Dossier synthétique affiché
  styles/              Variables de thème et styles de base
  test/                Environnement de tests et fixtures de test
tests/e2e/             Parcours Playwright sur le front compilé
```

Les styles propres à une fonctionnalité sont placés à côté de ses composants.
Les variables communes de couleur et d'espacement vivent dans `styles/tokens.css`.
Les couches CSS `tokens`, `base`, `components`, `layout`, `features` et `classic` définissent
une priorité explicite, pour que les règles d'adaptation des composants restent
effectives quand les fichiers de styles évoluent.
`styles/classic.css` reprend le thème de « Front init » et adapte les contrôles
React et les dialogues natifs à cette présentation.
La géométrie des icônes SVG est originale et centralisée ; les images et leur
provenance sont documentées dans [les ressources visuelles](RESSOURCES_VISUELLES.md).

Les composants reçoivent des données et des callbacks explicites. Le chargement
passe par `WorkspaceSource`, implémenté pour le dossier embarqué. Un futur
adaptateur local pourra remplacer cette source sans réécrire les panneaux.
Les entrées de source sont de type `unknown`, puis contrôlées avant affichage :
TypeScript ne dispense pas de vérifier les données reçues à l'exécution.

Les fonctions de contrôle, de résumé, de recherche et de cohérence du rapport
sont indépendantes de React. Les états restent auprès des composants qui les
utilisent ; aucun magasin global ni système de routage n'est ajouté pour cette
page unique. Les fonctionnalités futures pourront introduire un routage ou un
cache de données lorsque leurs besoins seront définis.

## Vérifications

Depuis `frontend/` :

```bash
npm run check
npx playwright install chromium
npm run test:e2e
```

`check` vérifie le formatage, exécute les tests Vitest / Testing Library,
contrôle les types stricts et compile la version de production. Les tests
couvrent le contrat de présentation, les empreintes, les décisions de revue,
les données absentes, la recherche, les logs et l'échappement des messages.

Playwright couvre le téléchargement exact, le focus des dialogues, le chat
agrandi, la navigation mobile et les différentes largeurs d'écran sur la version
compilée. Il démarre son propre serveur sur `127.0.0.1:4173`. Les traces et les
captures d'échecs restent sous `.argos/playwright-results/`, ignoré par Git.
L'installation du navigateur nécessite un téléchargement initial ; la CI
exécute ces mêmes vérifications sur Node.js 24.

Commandes de travail supplémentaires : `npm run test:watch`, `npm run typecheck`
et `npm run format`. Les tests du noyau restent indépendants :

```bash
python3 -m unittest discover -s tests -v
python3 scripts/check_repository.py
git diff --check
```

Ces trois commandes s'exécutent à la racine du dépôt. Les choix de contenu de
l'étape terminée sont conservés dans
[la revue historique de l'accueil](../archive/reviews/HOME_DESIGN_REVIEW.md).
Le raccordement à des missions locales réelles reste un livrable séparé.
