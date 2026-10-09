# Premier livrable — Argos Core hors ligne

**Version :** 1.0. **Date :** 7 octobre 2026.
**Autorisation :** proposition acceptée par le propriétaire dans la conversation.

## Objectif

Fournir une première CLI originale et reproductible : créer une mission, importer
des constats synthétiques, vérifier les preuves locales, enregistrer une revue
humaine et produire un rapport Markdown. Ce livrable amorce les fondations
d'Argos ; il ne valide pas l'ensemble de `01_SCOPE_V0_ARGOS.md`.

## Décisions de cette tranche

- Nom du produit : Argos. Nom technique du noyau : Argos Core.
- Python 3.11 ou supérieur, bibliothèque standard, lancement `python3 -m argos`.
- Modules séparés pour la CLI, le stockage, la validation et le rapport.
- Documents JSON versionnés (`schema_version: 1`) ; pas de base de données.
- Preuves locales : chemin relatif à une racine explicite, provenance et SHA-256.
- Aucun accès réseau, modèle IA ou lancement des supports importés dans ce lot.
- Tests `unittest` et CI sur Python 3.11, 3.12 et 3.13.

## Contrat de données

Le schéma est [assessment.schema.json](../../schemas/assessment.schema.json).
Chaque document contient une mission (`id`, `title`, `description`, `scope`),
des preuves (`id`, `path`, `sha256`, `description`, `source`) et des constats
(`id`, `title`, `severity`, `asset`, `description`, `recommendation`,
`evidence_ids`, `review`). Les champs inconnus sont refusés.

Un constat vise un actif déclaré dans le scope, cite au moins une preuve
existante et possède une revue nulle ou une décision `accepted` / `rejected`
accompagnée d'un nom de relecteur et d'une justification. La revue est une
déclaration humaine enregistrée ; elle n'est ni authentifiée ni signée. Une
preuve intègre ou une décision `accepted` ne confirme pas techniquement une
vulnérabilité. Le rapport conserve les constats rejetés et ceux à revoir.

Les identifiants sont uniques dans chaque collection. Les preuves sont des
fichiers ordinaires dans la racine choisie ; chemins absolus, traversées de
répertoire et liens sortant de cette racine sont refusés. Le JSON est limité à
1 MiB, chaque preuve à 5 MiB. Les doublons de clés JSON et nombres non standard
sont refusés. Le rapport affiche les métadonnées des preuves, pas leur contenu.

## Interface et sorties

| Commande | Résultat |
| --- | --- |
| `init` | Nouveau document avec une mission et des collections vides |
| `import` | Nouvelle copie de la mission enrichie depuis un document de la même mission et du même scope ; collisions d'identifiants refusées |
| `validate` | Vérification du format, des références, du scope et des fichiers de preuve |
| `review` | Nouvelle copie avec une décision explicite sur un constat |
| `report` | Rapport Markdown déterministe ; stdout ou fichier |

Les sources restent intactes. Un fichier de sortie existant est refusé sauf
option `--force` ; même avec cette option, une source ou une preuve ne peut pas
être écrasée. `--evidence-root` indique où lire les preuves, par défaut le dossier
du document importé ou rapporté. Après déplacement d'un document, conserver la
racine des preuves en la passant explicitement.

Codes de sortie : `0` succès ; `2` erreur d'arguments ou de validation ; `1`
erreur de lecture ou d'écriture. Aucun rapport n'est produit depuis une entrée
invalide. Les valeurs utilisateur sont échappées dans le Markdown.

## Acceptation

1. Depuis un clone propre, une commande documentée génère le rapport de référence
   depuis les exemples synthétiques, sans installation de dépendances.
2. Deux exécutions de la même entrée produisent les mêmes octets.
3. Une preuve absente, modifiée ou extérieure à la racine empêche l'export.
4. Une référence inconnue, un actif hors scope, un identifiant dupliqué ou une
   entrée mal formée est refusé avec une erreur utile.
5. Une revue humaine apparaît dans le rapport sans devenir une confirmation
   automatique de vulnérabilité.
6. Le parcours `init → import → review → report`, la protection des sources et
   le rapport de référence sont couverts par des tests exécutables hors ligne.

## Suite du travail

Prochaine tranche proposée : persistance et reprise de missions, puis assistant
de triage sur constats importés. L'IA, l'interface Web et l'analyse statique
restent des lots séparés, avec leurs critères d'acceptation.
