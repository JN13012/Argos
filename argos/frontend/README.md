# Frontend ARGOS — documentation historique

Le projet React + TypeScript + Vite est sous `argos/frontend/`. Son point
d’entrée actuel est une page d’accueil minimale qui vérifie `GET
/api/v1/health`. Les anciens composants, fixtures et assets décrits ci-dessous
sont conservés comme travaux historiques, mais ne sont pas montés par
l’application actuelle et ne doivent pas être considérés comme des fonctions
disponibles.

Les styles et les ressources sont locaux ; aucune police distante ni CDN.

## Version intégrée

Le frontend historique avait été repris dans ce dépôt avec la nouvelle composition
de l’accueil : une scène Three.js / React Three Fiber, un globe central et des
placeholders pour le loup et le Kraken. La boucle dure 48 secondes ; elle peut
être mise en pause, s’arrête hors écran et respecte la réduction du mouvement.

Les personnages détaillés sont une production séparée. OSINT, Blue Team et
Red Team restent des destinations à venir. Le dossier affiché est fictif ;
le chat utilise des réponses locales prédéfinies. Le moteur OSINT Python actuel
n’est pas encore connecté au frontend.

Le lancement local préparé pour ce dépôt se fait depuis sa racine avec :

```bash
bash argos/frontend/start-local.sh
```

Lancer d’abord l’API dans un autre terminal avec `bash scripts/dev-api.sh`.
Ouvrir http://localhost:8013/ dans Chrome. Le script utilise le Node.js local
préparé sous `.argos/frontend-tooling/` lorsqu’il est disponible.

Voir [le plan](../../docs/development/frontend/PLAN_FRONTEND.md) et
[le brief des mascottes](../../docs/development/frontend/BRIEF_ASSETS_3D.md).

## Lancer le front

Node.js **24.15 ou supérieur** et npm sont nécessaires :

```bash
cd argos/frontend
npm ci
npm run dev
```

Ouvrir **http://localhost:8013**. Le serveur écoute uniquement sur `127.0.0.1`.
Arrêter avec `Ctrl+C`. L'installation initiale récupère les dépendances npm.
Une fois les dépendances disponibles, le dashboard fonctionne localement sans
clé d'API ni accès à un service externe.

Pour consulter la version compilée :

```bash
npm run build
npm run preview
```

`dist/` est généré et ignoré par Git. L'ouverture directe de `index.html` avec
`file://` et l'ancien serveur Python pointant sur le frontend ne conviennent plus
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

Les styles suivent une organisation hybride, sans bibliothèque supplémentaire :

- Tailwind CSS 4 définit les boutons, badges et champs. Le lien de téléchargement
  utilise la même définition que les boutons ; chaque variante possède ses
  propres dimensions et couleurs, sans superposition de classes concurrentes.
- `styles/tokens.css` conserve les valeurs partagées existantes.
  `styles/utilities.css` les expose à Tailwind et définit les couleurs des
  contrôles. Une couleur partagée doit venir du thème, sans être recopiée dans
  plusieurs composants.
- Le CSS des fonctionnalités reste à côté de leurs composants : disposition,
  variantes de contexte, mascottes et scène 3D. Chaque groupe de styles a un
  propriétaire : en-tête dans `AppShell.css`, bandeau dans `HomePage.css`,
  grille dans `DashboardLayout.css`, chat dans `ChatPanel.css`. Le fichier
  historique de corrections `premium.css` a été retiré.
- L’ordre des couches est `theme, tokens, base, components, utilities, layout,
features`. Les utilitaires fournissent les styles communs ; les variantes
  de contexte définies dans le CSS restent prioritaires. Les règles responsive
  suivent les styles par défaut dans leur fichier propriétaire.

Les classes `button`, `button--*` et `badge` servent uniquement aux adaptations
de contexte existantes. Elles ne redéfinissent pas les styles communs de Tailwind.
Ne pas ajouter une seconde définition globale ou une bibliothèque de fusion de
classes pour contourner un conflit : corriger la règle à sa source.
La géométrie des icônes SVG est originale et centralisée ; les images et leur
provenance sont documentées dans [assets/README.md](assets/README.md).

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

Depuis `argos/frontend/` :

```bash
npm run check
npx playwright install chromium
npm run test:e2e
```

`check` vérifie le formatage, exécute les tests Vitest / Testing Library,
contrôle les types stricts et compile la version de production. Les tests
couvrent le contrat de présentation, les empreintes, les décisions de revue,
les données absentes, la recherche, les logs et l'échappement des messages.

Playwright couvre le contrôle de santé API et la page d'accueil minimale sur
ordinateur et mobile. Il démarre l'API et son propre serveur web sur
`127.0.0.1:4173`. Les traces et les
captures d'échecs restent sous `.argos/playwright-results/`, ignoré par Git.
L'installation du navigateur nécessite un téléchargement initial ; la CI
exécute ces mêmes vérifications sur Node.js 24.

Commandes de travail supplémentaires : `npm run test:watch`, `npm run typecheck`
et `npm run format`. Les tests Python restent indépendants :

```bash
uv run pytest
uv run ruff check argos/backend
```

Ces commandes s'exécutent à la racine du dépôt. Les choix historiques de contenu
sont expliqués dans
[la revue de l'accueil](../../docs/development/frontend/HOME_DESIGN_REVIEW_HISTORIQUE.md).
Le raccordement à des missions locales réelles reste un livrable séparé.
