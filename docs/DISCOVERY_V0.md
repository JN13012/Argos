# Discovery V0 — prototype local de qualification

**Date :** 8 octobre 2026. **Contrat :** `schema_version: 1`.
**Scoring :** `conservative-v1`. Cette tranche est autorisée par la demande actuelle.

## Périmètre séparé

Le dépôt possède déjà Argos Core hors ligne et un dashboard React. Discovery
ajoute une tranche indépendante de découverte d'entreprises professionnelles
publiques, enrichissement HTML limité et qualification explicable.

**Contradiction documentée :** la section 15.2 de `01_SCOPE_V0_ARGOS.md` exclut
l'enrichissement commercial de l'OSINT technique. Discovery étend aussi la stack
et l'accès réseau au-delà de `docs/FIRST_DELIVERABLE.md`. Cette fiche enregistre
cette différence sans réécrire la vision ni valider le draft V0. Un rattachement
au produit reste une décision à formaliser.

Les cinq commandes hors ligne et leur contrat `assessment.schema.json` sont
conservés. Discovery utilise [discovery.schema.json](../schemas/discovery.schema.json).
Il n'utilise ni le dashboard, ni les imports `Harness/`, ni un modèle IA.
Il ne réalise aucun scan/test d'intrusion et n'envoie aucun message commercial.

## Architecture

```text
SearchQuery -> DiscoveryProvider -> normalisation + déduplication
            -> sites déclarés -> WebEnricher -> contacts normalisés
            -> scoring déterministe -> DiscoveryResult -> SQLite / CLI / JSON
```

`argos/discovery/` contient `models.py`, `providers.py`, `normalize.py`,
`http.py`, `enrichment.py`, `scoring.py`, `service.py`, `repository.py` et
`cli.py`. Les interfaces `DiscoveryProvider` et `DiscoveryRepository` isolent
les fournisseurs et le stockage. `QueryInterpreter` prépare une conversion
ultérieure du langage naturel ; aucune implémentation IA n'est ajoutée.

SQLAlchemy 2 stocke des snapshots transactionnels dans `searches`, `businesses`,
`observations`, `enrichment_runs` et `scores`. `save` et `load` reconstruisent
le résultat public complet. Une nouvelle recherche n'écrase pas les précédentes.
Pas de migrations entre versions de schéma dans ce prototype.

## Installation et lancement

Discovery nécessite **Python 3.12+** et `uv`. Le noyau hors ligne reste utilisable
avec Python 3.11+ et la bibliothèque standard. Depuis le checkout :

```bash
uv sync --locked
uv run argos discover businesses --activity "garage automobile" \
  --location Marseille --demo --limit 20 \
  --opportunity website --opportunity ai --opportunity cybersecurity \
  --json .argos/discovery-demo.json
```

Le mode `--demo` utilise les [fixtures synthétiques](../examples/discovery/README.md)
sans DNS ni HTTP réel après installation. Les scores sont reproductibles ;
les identifiants d'exécution et temps approximatifs peuvent varier :

```text
Company                    Website  AI  Cyber  Confidence
Garage Démo Sans Site            25   0      0          44
Garage Démo Classique            55  40     10          70
Garage Démo Moderne               0   0      0          70
Garage Démo Indisponible          0   0      0          50
```

Pour les APIs officielles, omettre `--demo` :

```bash
uv run argos discover businesses --activity "garage automobile" \
  --location Marseille --limit 20 --json .argos/marseille.json
```

`garage automobile` correspond à `45.20A` (NAF Rév.2, véhicules légers).
Un code explicite est accepté ; les autres expressions utilisent une recherche
textuelle annoncée comme incomplète. Le filtre API vise l'unité légale ; le
connecteur contrôle aussi l'activité de l'établissement local. La commune est
résolue avec l'API géographique ; codes postaux, commune et arrondissements sont
vérifiés. Une commune inconnue ou homonyme est refusée. La transition NAF 2027
nécessitera une révision explicite de la correspondance.

Le registre ne fournit pas systématiquement de site ou de contacts. **Aucun site
identifié ne prouve pas qu'aucun site existe.** Aucune URL ou adresse email n'est
inventée. Pour enrichir un site associé à un SIRET, passer
`--website-hints .argos/website-hints.json`. Format, avec valeurs fictives :

```json
[
  {
    "siret": "00000010200001",
    "website": "https://garage.example/",
    "source_url": "fixture:human-verified-association-example",
    "collected_at": "2026-10-08T00:00:00Z",
    "official_association_declared": true
  }
]
```

Pour des données réelles, utiliser une association et une référence vérifiées.
C'est une déclaration humaine, sans authentification de propriété (confiance 0,6).
Les SIRET dupliqués dans ce fichier sont refusés.

La base par défaut est `.argos/discovery.sqlite3` ; `--database` la personnalise.
`--skip-web` désactive l'enrichissement. Les scores non demandés sont `null`, la
confiance reste calculée. Les fichiers JSON existants et les sorties remplaçant
une entrée ou la base sont refusés : choisir un nouveau nom d'export.
Codes de sortie : `0` succès, `2` saisie/fournisseur, `1` stockage. Une erreur API
ne devient pas une recherche vide réussie. Le snapshot est sauvegardé avant
l'export : si l'export échoue, la recherche peut déjà être en base.

## Sources, provenance et contacts

Le connecteur suit le [contrat officiel](https://recherche-entreprises.api.gouv.fr/openapi.json)
de l'[API Recherche d'Entreprises](https://recherche-entreprises.api.gouv.fr/docs/)
et l'[API Découpage administratif](https://geo.api.gouv.fr/decoupage-administratif).
Les unités/établissements non diffusibles ou en diffusion partielle, inactifs,
entrepreneurs individuels et catégories juridiques inconnues sont exclus par
prudence. Les dirigeants et dates de naissance ne sont pas demandés/conservés.

Chaque champ sélectionné garde source, référence, date, valeur brute extraite,
valeur normalisée et confiance. Les métadonnées HTTP et SHA-256 des réponses sont
stockés ; les pages complètes ne sont pas archivées. Les contacts proviennent de
liens `tel:` français et `mailto:` à boîte générique (`contact`, `info`, etc.).
Les emails nominatifs sont exclus par heuristique ; cette règle n'est pas une
garantie juridique. Les liens sociaux sont référencés sans être visités.

Un modèle par entreprise conserve finalité, source/date du contact, type de
contact, `deleted_at` et `do_not_contact` (vrai par défaut). Il prépare un suivi
ultérieur, sans suppression effective, registre global d'opposition, chiffrement
de la base ou rétention automatique. Les données réelles restent sous `.argos/`,
ignoré par Git.

Un même SIRET est fusionné avec conservation des observations. Des SIRET
différents restent des branches distinctes ; deux SIREN différents ne sont pas
fusionnés. Sans identifiant contradictoire, nom + adresse + code postal servent
de repli. Un domaine seul ou des branches ambiguës avec même SIREN provoquent un
avertissement sans fusion. Un champ conflictuel d'un même SIRET conserve la
première valeur et les deux observations avec avertissement.

## Scores conservateurs

Chaque score est une somme bornée à 0–100. Les facteurs conservent poids,
explication et références d'observations. Zéro signifie « aucun facteur observé
dans cette collecte », pas « aucun besoin ». Aucun score ne prouve un besoin
commercial. Le cyber est une **potential cybersecurity service opportunity**,
jamais une mesure de vulnérabilité.

| Score | Facteur | Points |
| --- | --- | ---: |
| Website | Site non identifié dans les sources | 25 |
| Website | Homepage observée en HTTP | 15 |
| Website | Viewport absent du HTML de la homepage | 15 |
| Website | Meta description absente de la homepage | 10 |
| Website | Aucun formulaire/contact générique détecté | 10 |
| Website | Aucun lien de réservation détecté pour `45.20A` | 15 |
| AI | `45.20A` et aucun lien de réservation détecté | 20 |
| AI | Condition précédente et contact public | 10 |
| AI | Condition précédente et texte horaires/services | 10 |
| Cyber | Homepage observée en HTTP | 10 |
| Cyber | Échec explicite de vérification du certificat TLS | 15 |

Les facteurs d'absence nécessitent du HTML accessible. Une page interne en échec
rend la réservation inconnue. HTTP observé ne démontre pas l'absence de HTTPS.
Les technologies détectées restent des observations sans points cyber. Aucun
élément absent n'est présenté comme une vulnérabilité.

La confiance est indépendante : identité (10), SIRET (15), adresse (10), ville
(5), activité (5), site déclaré (10), chacun pondéré par sa confiance de source
et arrondi. Couverture HTML : 20, ou 10 si partielle. Ces poids ne sont pas
calibrés statistiquement et ne promettent pas de précision commerciale mesurée.

## Bornes réseau et limites

- GET uniquement ; aucun JavaScript, formulaire envoyé ou contenu téléchargé exécuté.
- Une requête à la fois ; quatre pages fournisseur de 25 unités légales maximum.
- Trois pages HTML et seize requêtes par site maximum, robots/redirections compris.
- Timeout HTTP de 5 s par phase ; délai de lecture du corps contrôlé.
- Réponses de 1 MiB maximum ; compression refusée ; User-Agent identifiable.
- TLS toujours vérifié. URLs HTTP/HTTPS, ports standards, aucun userinfo/contrôle.
- Toutes les adresses DNS doivent être publiques ; connexion à une IP vérifiée
  épinglée avec Host et nom TLS d'origine via l'[extension SNI HTTPX](https://www.python-httpx.org/advanced/extensions/).
  Pas de proxy d'environnement ; contrôles répétés à chaque redirection.
- Domaine initial et variante `www` seulement ; déclassement HTTPS vers HTTP refusé.
- robots.txt avant chaque origine, y compris après redirection. 404 autorise ;
  autres erreurs bloquent. Délais robots respectés jusqu'à 5 s, au-delà parcours
  refusé. Espacement minimal de 200 ms entre requêtes de pages.

La résolution système DNS n'a pas de délai strict imposé par ce prototype.
Les sites dynamiques, CDN exigeant compression et redirections vers un autre
domaine peuvent être incomplets. L'API bornée n'est pas un inventaire exhaustif.
Une erreur réseau ponctuelle ne décrit pas durablement l'état du site.
Une vérification manuelle le 8 octobre 2026 a enregistré trois établissements
marseillais depuis les deux APIs officielles, avec `--skip-web` et sans visiter
leurs sites. Cette vérification ponctuelle ne constitue pas un test d'intégration
réseau permanent ni une validation exhaustive du fournisseur.

## Vérification et suite

```bash
uv run pytest
python3 -m unittest discover -s tests -v
python3 scripts/check_repository.py
git diff --check
```

Les tests dans `tests_discovery/` interdisent sockets/DNS réels et couvrent
provenance brute, normalisation, scores, ambiguïtés, données exclues, géographie,
pagination, erreurs API/HTTP, absence/inaccessibilité de site, robots/SSRF,
tailles, export, snapshots/transactions SQLite et contrat JSON.
La CI Discovery utilise Python 3.12/3.13 ; la CI du noyau conserve 3.11/3.12/3.13.

Suite recommandée : code commune pour lever les homonymies, davantage de variantes
API et révision NAF avant 2027, suppression/rétention/opposition, source fiable de
sites et calibration sur qualifications humaines. Un test live doit rester
optionnel. Aucun Google Maps, scraping LinkedIn, campagne, PostgreSQL, framework
d'agents ou raccordement au dashboard dans ce lot.
