# ARGOS — Brief 3D Mascottes

## Objectif
Produire deux assets 3D animables pour le frontend :
- Blue Team : loup humanoïde musclé
- Red Team : Kraken biomécanique

Le rendu doit être premium, crédible pour portfolio / LinkedIn / recruteurs, et optimisé pour le web.

---

## Direction artistique commune

- style semi-réaliste / stylisé premium
- base sombre graphite / noir
- cybernétisation légère à modérée
- pas de look “robot complet”
- pas de style cartoon
- matériaux lisibles et cohérents
- détails lumineux utilisés avec parcimonie

### Blue Team
- accents bleu électrique
- fourrure gris foncé / gris clair
- armure tactique graphite
- silhouette massive, musclée, protectrice

### Red Team
- accents rouge profond
- peau sombre organique
- plaques biomécaniques graphite
- silhouette menaçante mais élégante
- tentacules clairement lisibles

---

## Asset 1 — Loup Blue Team

### Modèle
- humanoïde
- corps entier
- environ 2,2 m
- musculature marquée
- fourrure visible
- plastron / épaules / avant-bras / jambes légèrement blindés
- queue complète
- yeux bleus émissifs

### Rig
- humanoid skeleton
- tête / cou
- colonne
- bras / mains / doigts
- jambes / pieds
- queue
- oreilles
- mâchoire légère
- yeux orientables

### Animations
- idle
- walk
- alert
- scan
- defend / response

### Capacité spéciale
Scan oculaire :
- intensification des yeux
- faisceaux bleus projetés
- tête orientable vers cible
- compatible avec effets Three.js côté frontend

---

## Asset 2 — Kraken Red Team

### Modèle
- corps principal compact
- tête / manteau massif
- 4 à 6 tentacules principales animables
- tentacules secondaires plus simples
- ventouses détaillées
- plaques biomécaniques discrètes
- yeux rouges émissifs

### Rig
- tête
- yeux
- déformation légère du corps
- chaînes de bones par tentacule
- IK / spline si pertinent
- extrémités contrôlables indépendamment

### Animations
- idle
- tentacle_reach
- probe
- attack / pressure
- retract

### Capacité spéciale
Interaction avec globe :
- 1 à 2 tentacules ciblent une zone
- glow rouge augmente
- ventouses pulsent légèrement
- mouvement lent et contrôlé

---

## Contraintes techniques

### Format
- export final : GLB
- unités cohérentes
- transformations appliquées
- pivot propre
- orientation standard
- animations nommées clairement

### Optimisation web
- topologie propre
- limiter le nombre de bones
- textures compressées
- éviter les shaders trop lourds
- prévoir LOD si nécessaire
- conserver silhouette et visage en priorité

### Textures
- PBR
- Base Color
- Normal
- Roughness
- Metallic
- Emissive

Résolutions raisonnables :
- 2K pour corps principal
- 1K pour secondaires si possible

---

## Intégration frontend prévue

Stack cible :
- Three.js
- React Three Fiber
- GLTF / GLB
- animations pilotées par états

Exemple :

idle
osint_scan
red_probe
blue_response

Le frontend doit pouvoir :
- lancer une animation spécifique
- faire apparaître / disparaître une mascotte
- orienter tête / regard
- contrôler certaines tentacules
- ajouter effets lumineux séparément