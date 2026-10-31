# Argos — production des mascottes 3D

## Décision de travail

Produire le loup Blue Team et le Kraken Red Team séparément, avec une direction
artistique et un contrat d’intégration communs. Les assembler ensuite dans la
scène existante autour du globe. Ne pas fusionner les deux personnages et le
globe dans un unique fichier de scène.

Le frontend actuel conserve le globe, la composition, la boucle de 48 secondes,
les fondus, les contrôles de pause et les règles de visibilité. Les personnages
géométriques actuels servent uniquement de placeholders. Leur apparence ne fait
pas partie de la direction artistique finale.

## Référence artistique

Référence principale :
`C:/Users/Cyber/Documents/WorkShop/Argos/logo/Tableau HUD Sci‑Fi _ ARGOS et Équipes Néon.png`.

Retenir les volumes, l’anatomie et la présence de cette planche. Le loup est
humanoïde et musclé, comme dans la référence. Le personnage Red Team reprend
la présence organique et les appendices de la référence Kraken / Cthulhu.
Les éventuelles ailes doivent rester contrôlables et ne pas masquer le globe.

Style partagé : graphite, noir bleuté, métal sombre et tissus organiques riches.
Cybernetique discrète, concentrée dans quelques pièces et lignes lumineuses.
Yeux lumineux, surfaces lisibles, formes détaillées et silhouettes reconnaissables.
La fourrure, les plis et les petites pièces doivent apporter du relief sans
saturer le cadre. Éviter de répartir la lumière sur toutes les arêtes.

Les images sont des références artistiques. Elles ne constituent pas un modèle
3D, une topologie de production ou un squelette d’animation.

## Loup Blue Team

- Corps entier, anatomie musclée et crédible, tête expressive et mâchoire lupine.
- Fourrure sombre maîtrisée ; une partie du détail sera portée par les textures.
- Pièces cybernétiques sobres sur épaules, torse ou membres ; visage identifiable.
- Accents bleus et yeux lumineux, suffisamment retenus pour conserver la matière.
- Posture de garde ; épaules, cou, tête et bras articulables.
- Le modèle complet doit fonctionner sur sa future page dédiée. La homepage
  pourra en cadrer seulement le buste sans créer un autre personnage.

Premiers clips proposés : `Idle` (respiration lente), `Activate` (tête qui se
redresse), `Protect` (posture de protection), `Settle` (retour au repos).

## Kraken Red Team

- Volumes organiques, crâne et silhouette détaillés, matière sombre légèrement
  humide avec une rugosité contrôlée.
- Tentacules distincts, départs anatomiques crédibles et transitions propres.
- Cybernétique légère ; accents rouges et yeux lumineux.
- Chaque tentacule principal possède une chaîne d’os permettant un mouvement
  préparé, sans calcul de physique dans le navigateur.
- Si les ailes de la référence sont conservées, prévoir leur articulation et
  une pose repliée compatible avec le bandeau.

Premiers clips proposés : `Idle` (mouvements organiques très faibles), `Activate`,
`Reach` (approche du globe), `Settle` (rétraction calme).

## Production et validation

1. **Références propres** : face, profil et trois-quarts de chaque personnage ;
   fixer l’anatomie, les proportions et les matériaux. Commencer par le loup.
2. **Modélisation détaillée** : produire le modèle maître dans Blender ou un
   outil 3D adapté. Une base générée peut accélérer ce travail, mais elle doit
   être inspectée et retouchée avant validation.
3. **Version web** : préparer une topologie adaptée aux déformations, les UV et
   des textures PBR. Reporter les microdétails dans les normal maps lorsque cela
   convient. Tester le matériau exporté dans Three.js dès cette étape.
4. **Squelette et animations** : ajouter le rig, ajuster les poids de déformation,
   produire les clips et vérifier les poses extrêmes. Ne pas confondre un modèle
   riggable et un modèle effectivement riggé et animé.
5. **Validation artistique** : examiner le loup sous l’éclairage du front et dans
   un cadrage de portfolio. Utiliser ce premier modèle comme référence de qualité
   pour produire le Kraken.
6. **Intégration** : importer les GLB un par un, puis tester la composition avec
   le globe. Ajuster seulement le cadrage, les offsets et la taille des personnages
   si nécessaire ; garder la logique de boucle.

## Contrat de livraison

Pour chaque personnage : source éditable `.blend`, textures, GLB de production
et liste des clips. Export glTF 2.0 avec matériaux PBR compatibles, squelette
et animations conservés. Les contrôleurs propres au logiciel de création doivent
être convertis en animations exportables si nécessaire.

- Unités définies en mètres ; export orienté avec +Y vers le haut et face vers +Z.
- Origine et pivot documentés. Le fichier maître conserve une pose et un squelette
  propres ; le frontend applique son cadrage dans un groupe parent.
- Noms stables des meshes et matériaux, en distinguant au minimum peau/fourrure,
  pièces cybernétiques et éléments lumineux.
- Transformations cohérentes et géométrie sans pièces perdues ni normales inversées.
- Les modèles sont autonomes et n’embarquent pas le globe, les lumières ou la caméra
  du frontend.
- Les animations de personnage ne pilotent pas la caméra ni la boucle de page.

Organisation proposée :

```text
assets-3d/
  wolf-blue/
    references/
    source/wolf-blue.blend
    textures/
    exports/wolf-blue.glb
    animations.md
  kraken-red/
    references/
    source/kraken-red.blend
    textures/
    exports/kraken-red.glb
    animations.md
```

Les exports validés pourront être copiés sous `argos/frontend/public/models/`.
Ces chemins décrivent les futurs livrables : aucun GLB détaillé n’est encore produit.

## Qualité et performance

Conserver une source détaillée et préparer une version web adaptée au cadrage.
Première enveloppe de travail indicative par personnage : environ 30–60 mille
triangles pour la version web, textures jusqu’à 2K et un petit nombre de matériaux.
Ce sont des cibles de départ à ajuster après mesure, pas une garantie de fluidité.

Évaluer le poids transféré, le coût de décodage, la mémoire des textures sur le GPU,
le nombre d’appels de rendu et le coût du squelette. Tester un ordinateur modeste
et un mobile physique avant de valider les deux personnages ensemble.

Un modèle allégé de homepage peut être dérivé du même maître si nécessaire.
La qualité du personnage est également validée en grand format, pour les futures
pages dédiées et les images de portfolio.

## Adaptation minimale du frontend

Remplacer les meshes placeholders par les modèles importés dans les groupes
parents déjà animés. Conserver le timing, les fondus, la rotation du globe et
les protections de performance. Ajouter la lecture des clips avec un mixer
d’animation, actif seulement pendant les phases visibles et non mises en pause.

Le fondu des personnages doit respecter les opacités et matériaux d’origine,
y compris les éventuels éléments de fourrure découpée et les parties lumineuses.
Les corps ne doivent pas pénétrer le globe ; les tentacules sont ajustés dans
les clips plutôt que résolus par une simulation physique.

## Documentation de référence

- Export Blender glTF : https://docs.blender.org/manual/en/5.1/addons/import_export/scene_gltf2.html
- Import Three.js : https://threejs.org/docs/pages/GLTFLoader.html
- Lecture des animations : https://threejs.org/manual/pages/animation-system.html
