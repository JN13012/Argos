# Fixtures Discovery

Entreprises, identifiants, adresses, contacts et sites **entièrement synthétiques**.
Aucun enregistrement officiel ni prospect réel. Les domaines `.example` sont
réservés à la documentation ; le mode `--demo` utilise HTTPX MockTransport et
un résolveur injecté, sans DNS ou HTTP réel.

`companies.json` reprend uniquement les champs administratifs utilisés du
contrat de l'API française. Un doublon teste la fusion d'un même SIRET.
`website-hints.json` simule des associations de sites déclarées ; `pages.json`
couvre un site simple en HTTP, un site avec lien de réservation, et un site
indisponible. Les snapshots générés restent sous `.argos/`.

```bash
uv sync --locked
uv run argos discover businesses --activity "garage automobile" \
  --location Marseille --demo --json .argos/discovery-demo.json
```
