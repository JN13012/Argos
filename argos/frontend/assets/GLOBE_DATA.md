# Géométrie du globe

Les côtes proviennent de `world-atlas`, fichier `land-110m.json`, dérivé des
données Natural Earth. Elles sont préparées par `scripts/build-globe-data.mjs`
en coordonnées longitude/latitude et projetées sur la sphère une seule fois.

- Source : https://github.com/topojson/world-atlas
- Données originales : https://www.naturalearthdata.com/
- Licence du paquet `world-atlas` : ISC ; données Natural Earth : domaine public.

Les points et connexions de la scène servent à l’ambiance du prototype et ne
représentent pas une collecte réelle. Le loup et le Kraken sont des sculptures
géométriques originales créées en code, destinées à être remplacées par les
modèles GLB définitifs.
