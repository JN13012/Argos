# Argos — plan de reprise du frontend

## Périmètre validé

Le prototype porte uniquement sur l’accueil. La navigation de gauche reste
l’unique accès aux domaines. OSINT, Blue Team et Red Team sont visibles, mais
leurs accès sont désactivés et portent la mention « À venir ». Les autres
espaces métier restent également désactivés.

La copie de travail reprend le frontend React/TypeScript/Vite du commit
`14d2bc149eab42e2b9eaf51680d4c2338179727d` du dépôt JN13012/Argos.
Le dépôt de travail OSINT et ses modifications locales ne sont pas modifiés.

## Direction visuelle

- Fond graphite, surfaces opaques, contours discrets et hiérarchie lisible.
- Violet OSINT, bleu Blue Team et rouge Red Team ; ambre pour les découvertes.
- Le globe est le fil conducteur d’une scène 3D discrète, placée à droite du
  bandeau. Les trois cartes illustrées ont été retirées à la demande de l’utilisateur.
- La scène alterne globe OSINT seul, globe accompagné du Kraken rouge,
  globe accompagné du loup bleu, puis globe seul.
- Le loup et le Kraken sont des sculptures géométriques provisoires ; les
  modèles détaillés de la planche de référence restent à produire en GLB.
- Une identité spectaculaire dans le bandeau ; une interface sobre pour travailler.
- Aucune statistique de sécurité réelle inventée : les données du dossier sont
  celles de la démonstration historique, explicitement identifiées.

## Étapes et critères de validation

1. **Accueil 2D** : récupération du front, palette commune, trois mascottes,
   navigation désactivée pour les espaces à venir. Vérifier bureau/mobile,
   clavier, dialogues, recherche et absence de débordement.
2. **Essai 3D de l’accueil** : une scène Three.js/React Three Fiber avec le globe
   et les deux compagnons provisoires. Fondus coordonnés dans une boucle de
   rendu unique ; GSAP pourra servir aux transitions de caméra plus élaborées.
   Prévoir une vue fixe de secours et mesurer le coût avant d’étendre la scène.
3. **Espace OSINT** : définir le contrat avec le moteur actuel, puis connecter
   une recherche et ses résultats réels. Retirer la démonstration historique.
4. **Personnages 3D** : modèles GLB et animations préparées pour le loup et Cthulhu.
   Ajouter seulement les animations utiles et valider leur coût.
5. **Blue Team et Red Team** : implémenter les pages selon les fonctions disponibles.

## Organisation technique

- Conserver React/TypeScript/Vite et les composants utiles du frontend récupéré.
- Introduire Tailwind sur les nouveaux éléments ; adopter shadcn/ui au besoin
  pour les nouveaux composants interactifs, avec le thème Argos.
- Garder les données, le chargement et les contrôles indépendants de la présentation.
- Aucun backend, authentification, déploiement ou publication dans l’étape 1.

## Règles de performance

L’utilisateur a choisi une boucle d’ambiance continue. Elle nécessite des
calculs tant qu’elle est visible et en lecture. Le cycle dure 48 secondes :
12 secondes OSINT, 12 Red, 12 Blue, puis 12 de retour au globe.

- Une seule scène et un rendu à la demande, alimenté au maximum 30 fois par seconde.
- Mise en pause manuelle, hors écran et dans un onglet masqué. Le temps de la
  scène est conservé : elle reprend au même endroit sans saut temporel.
- Respect de « réduire les animations », avec possibilité de reprise explicite.
- Géométrie du globe, côtes, arcs, sculptures et tentacules préparés à l’avance.
- Rotation et opacité mises à jour directement dans Three.js ; React ne reçoit
  un changement d’état qu’au passage d’une phase à une autre.
- Résolution plafonnée et réduite sur les appareils modestes ; aucun effet de
  post-traitement, ombre dynamique ou simulation de physique.
- Chargement différé du moteur 3D et globe vectoriel fixe si WebGL est indisponible.

Avant validation 3D : tester au moins un ordinateur modeste et un mobile réel.
Les objectifs de fluidité et de poids seront chiffrés après mesure du prototype.

## Historique de l’étape 1

L’accueil 2D est prêt à être examiné. Tailwind est configuré pour les nouveaux
éléments ; les composants interactifs historiques sont conservés.

Vérifications : compilation et contrôle des types réussis, 29 tests unitaires,
11 parcours navigateur réussis, mise en page contrôlée de 320 à 1 920 pixels.
Les contrôles de mise en page et de chargement ont été rejoués après les derniers
ajustements visuels. Les captures sont `preview-desktop.png` et `preview-mobile.png`.

## Révision de la composition

L’accueil a été révisé en une scène 3D compacte. Les cartes redondantes ont été
retirées. La boucle et les garde-fous sont implémentés dans la copie locale.

La prochaine étape artistique sera la production des modèles GLB détaillés,
après validation de la place et du rythme de cette scène.

La production des personnages est maintenant organisée séparément du frontend,
selon [le brief des assets 3D](BRIEF_ASSETS_3D.md). Commencer par le loup comme
référence de qualité, puis produire le Kraken dans la même charte. La scène,
le globe et la logique de boucle sont conservés pendant ce travail.

Vérifications de cette révision : compilation et types réussis, 31 tests unitaires
réussis et 14 parcours navigateur validés, dont les parcours de scène et de mise
en page rejoués après corrections. La pause a été vérifiée par comparaison de
deux captures du canvas ; l’arrêt hors écran et la réduction du mouvement sont
couverts. Les tests couvrent les largeurs de 320 à 1 920 pixels. La validation
sur un mobile physique reste à réaliser avant d’ajouter les modèles détaillés.

Captures actuelles : `preview-desktop.png`, `preview-mobile.png`, `preview-red.png`
et `preview-blue.png`.
