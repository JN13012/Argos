# Revue du dépôt avant publication

**Date :** 7 octobre 2026. **Référence initiale inspectée :** `0fd37c5`.

## Mise à jour après retrait du course pack

Le propriétaire a supprimé `Harness/course-pack/` du dossier courant et demandé
le push du nettoyage. Les 40 fichiers source restants de cet import sont retirés
du prochain arbre Git ; le chemin est désormais ignoré. Les références du README
et des notices sont actualisées, et `doc/references/RELATED_PROJECTS.md` ajoute une revue
des projets voisins avec sources primaires.

`gh repo view` confirme que `JN13012/Argos` est **déjà public**, avec `main` comme
branche par défaut. Un fetch a confirmé l'alignement des quatre commits locaux
avec `origin/main` avant cette préparation. Le push demandé est un push normal
du commit de nettoyage : les anciennes missions et supports restent dans
l'historique. Les imports `Harness/Labs/` et `Harness/Harness/` sont toujours
présents et leurs droits restent à clarifier. Les constats ci-dessous décrivent
la préparation initiale et conservent leur contexte temporel.

Contrôles du prochain arbre : 102 fichiers suivis, dont 1 Python, 5 JSON et
27 JavaScript validés ; liens locaux et contrôles de whitespace Git valides ;
aucun fichier du course pack, de mission privée, ignoré ou `Zone.Identifier`
dans l'index. La recherche des motifs de secrets décrits plus bas ne trouve
aucune correspondance dans ces 102 fichiers. Les réglages personnels et le
sélecteur de mission restent sur disque.

Lors de l'implémentation du premier livrable, le propriétaire a déplacé
`Harness/Labs/` hors du projet : il s'agissait d'un exercice terminé, séparé du
harness. Son retrait est enregistré dans un commit distinct. Les constats
historiques ci-dessous restent datés de la préparation initiale ; la démo
originale Argos Core utilise ses propres données synthétiques.

## Situation constatée

- Branche `main`, remote `origin` déjà configuré vers `JN13012/Argos`.
- Quatre commits dans l'historique local ; état de travail propre avant cette revue.
- 294 fichiers suivis initialement, dont 93 fichiers `Zone.Identifier`.
- Aucun `.gitignore`, README ou fichier de licence à la racine.
- 65 fichiers de missions suivis, plus un sélecteur de mission actif et des
  réglages Claude locaux. Les missions contiennent des journaux de requêtes,
  preuves, rapports, captures, archives et fichiers temporaires.
- Les documents de statut et le manifeste indiquaient encore que le scope V0
  devait être créé, alors que sa version 1.0 existe et reste `IN_PROGRESS`.

## Préparation réalisée

- Suppression des 93 fichiers de métadonnées Windows.
- Ajout d'un `.gitignore` couvrant les environnements, dépendances, caches,
  secrets locaux, sorties de missions et réglages personnels.
- Retrait de l'index des fichiers de missions, du sélecteur actif et des
  réglages locaux ; conservation sur disque de 66 fichiers hors métadonnées.
  Le modèle `_template` reste suivi. Les 159 retraits de l'index sont préparés
  pour le prochain commit ; aucun commit n'a été créé.
- Ajout d'un README, d'une proposition de progression, d'une notice d'origine
  des imports et d'un contrôle du dépôt utilisable hors ligne.
- Mise à jour du statut documentaire sans validation implicite du scope V0.

## Points à résoudre avant publication publique

1. **Historique :** les données de missions restent dans les anciens commits.
   Un prochain commit de nettoyage ne les efface pas. Choisir explicitement
   entre une nouvelle histoire publique depuis un export propre et un nettoyage
   coordonné de l'historique existant. Aucune réécriture ni publication n'a été
   effectuée pendant cette préparation.
2. **Provenance :** les supports et l'application de cours n'ont pas de licence
   identifiée dans le dépôt. Clarifier la source et les permissions avant de
   republier ces imports ou de choisir une licence globale.
3. **Reproductibilité :** `package.json` du laboratoire référence
   `test/unit.js`, absent du dépôt. Le README du cours décrit un répertoire
   `project/harness/` et un `system_prompt.md` absents ; `agent.py` est en réalité
   dans `Harness/course-pack/`. Les instructions importées ne constituent donc
   pas un parcours d'installation Argos vérifié.
4. **Maturité :** les profils et hooks restent expérimentaux. Le hook de scope
   décrit lui-même ses limites ; la plateforme et ses garanties annoncées dans
   le brief ne sont pas démontrées par ce dépôt.

## Vérifications et portée

- `git fsck --full` : aucune erreur signalée.
- Syntaxe avant nettoyage : 2 fichiers Python, 12 JSON, 27 JavaScript et
  4 JSONL contrôlés sans erreur. Aucun harness ou laboratoire exécuté.
- Recherche ciblée dans 188 blobs de l'historique local : aucun marqueur de clé
  privée ou jeton correspondant aux motifs GitHub, AWS `AKIA` et `sk-` contrôlés.
  Cette recherche limitée ne détecte pas tous les secrets, cookies, identifiants,
  données personnelles ni formats binaires et ne certifie pas leur absence.
- Le script `scripts/check_repository.py` vérifie le contenu public courant et
  les chemins sensibles suivis ; il ne scanne pas les anciens commits. Après
  nettoyage : 3 Python, 7 JSON et 27 JavaScript vérifiés sans erreur ; aucun
  fichier ignoré encore suivi ; aucun `Zone.Identifier` restant ; huit cas
  représentatifs du `.gitignore` et les liens locaux des nouveaux documents
  vérifiés. Les contrôles de whitespace Git passent.
- Aucun test fonctionnel, audit complet des dépendances ou comparaison de
  performance n'a été effectué. La première préparation n'avait ni consulté la
  visibilité distante ni effectué de push ; la vérification distante et le push
  de nettoyage font l'objet de la mise à jour ci-dessus.
