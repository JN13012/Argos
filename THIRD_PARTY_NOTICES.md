# Origine des éléments importés

Le dépôt contient des éléments pédagogiques importés. Leur présence ne signifie
pas qu'ils ont été écrits pour Argos ni que leur redistribution est autorisée.

| Chemin | Indices disponibles dans le dépôt | État |
| --- | --- | --- |
| `Harness/course-pack/` | Formation TryHackMe « Supercharging Your Pentesting With AI », identifiée par le propriétaire ; README correspondant | Retiré du dossier courant par le propriétaire le 7 octobre 2026 ; encore dans l'historique Git |
| `Harness/Labs/lab2-source/` | Application de formation « Brayford Mutual », importée avec les supports | Exercice terminé, déplacé hors du dépôt par le propriétaire ; conservé dans l'historique Git |
| `Harness/Harness/` | Profil expérimental associé au cours, avec adaptations locales | Séparer l'origine du cours et les adaptations |

La revue du 7 octobre 2026 n'a trouvé aucun fichier `LICENSE` ou `COPYING` suivi
dans ce dépôt. Le message du commit d'import mentionne un cours, mais ne permet
pas à lui seul de documenter les droits de redistribution.

Le propriétaire a ensuite déplacé `Harness/Labs/` hors du projet, car il
s'agissait d'un exercice terminé sans rapport avec le harness. `Harness/Harness/`
reste une référence expérimentale dont la provenance est à clarifier. Le dépôt
distant est déjà public ; ces retraits ne purgent pas les imports des anciens
commits.

Avant publication publique, renseigner pour chaque import : source exacte,
auteur, version ou date, licence ou autorisation, attribution demandée et
modifications locales. En l'absence de clarification, préparer une version
publique sans les éléments concernés et conserver ces références localement.

Une licence choisie pour le code original d'Argos devra préciser son périmètre et
respecter les notices des composants tiers. Ce fichier ne leur attribue aucune
licence.

Le propriétaire a fourni le chemin d'une capture de certification THM lors de la
préparation. Cette indication documente le contexte du cours ; la capture n'a
pas été consultée et les conditions de redistribution restent à établir.
