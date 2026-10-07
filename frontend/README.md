# Accueil Argos

Prototype du dashboard d'accueil, reconstruit à partir des propositions visuelles
fournies par le propriétaire. Fond bleu nuit, accents cyan, mascotte Argos,
navigation latérale, indicateurs, suivi des missions et panneau de chat.

## Ouvrir la démonstration

Depuis la racine du dépôt :

```bash
python3 -m http.server 8000 --bind 127.0.0.1 --directory frontend
```

Ouvrir **http://localhost:8000**. Arrêter le serveur avec `Ctrl+C`.
Il est également possible d'ouvrir directement `frontend/index.html` dans un
navigateur : les scripts classiques et les ressources relatives ne nécessitent
ni serveur d'API ni téléchargement de dépendances.

## Périmètre

Seul l'accueil est réalisé. La page s'adapte aux écrans de bureau, tablettes et
téléphones. La recherche (`Ctrl+K` ou `Cmd+K`), l'aperçu de mission, les
notifications, le filtrage du journal, le téléchargement du rapport et le chat
de démonstration sont utilisables. Le chat peut être agrandi ; `Échap` le réduit.

Les espaces Red Team, OSINT, Blue Team, Preuves, Rapports, Agents et Paramètres,
ainsi que la création de mission, sont présentés dans la navigation mais ne
sont pas implémentés. Leurs boutons sont désactivés.

## Données et fonctionnement

- `demo-data.js` contient une copie du document synthétique
  `examples/offline/assessment.json` ; les titres et descriptions de l'aperçu
  sont présentés en français. Une mission, un actif, deux constats à revoir,
  deux preuves référencées, aucun constat critique et aucun agent connecté.
- `assets/demo-report.md` est une copie du rapport de référence du même exemple.
  Le téléchargement ne génère pas un nouveau rapport.
- Le journal illustre ce document ; ses numéros sont des étapes d'exemple, pas
  des événements d'un moteur en cours d'exécution.
- Le chat répond avec des textes prédéfinis. Les messages sont conservés
  uniquement en mémoire et disparaissent au rechargement. Aucun appel à un
  modèle, accès aux preuves locales ou lancement d'outil n'est effectué.
- Le front n'est pas encore connecté à Argos Core. Le contrat de données,
  les commandes et les tests du noyau restent ceux du livrable hors ligne.

HTML, CSS et JavaScript sans dépendance, police distante ni CDN. Les ressources
visuelles sont décrites dans [assets/README.md](assets/README.md).

La prochaine tranche pourra connecter les données réelles de mission à cet
accueil, avant de développer les pages de mission et de revue.
