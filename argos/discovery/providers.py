"""The official French company provider, plus a strictly local demonstration."""

from datetime import datetime
import re

import httpx
from pydantic import ValidationError

from .http import FetchError, PublicHttpClient
from .models import ProviderBatch, ProviderError, SearchQuery, SourceReference, utc_now
from .normalize import match_text, normalize_establishment


ACTIVITIES = {"garage automobile": "45.20A", "garage": "45.20A", "garages automobiles": "45.20A"}


def activity_filter(activity: str) -> tuple[str, bool]:
    value = ACTIVITIES.get(match_text(activity))
    if value:
        return value, True
    if re.fullmatch(r"\d{2}\.\d{2}[A-Z]", activity.upper()):
        return activity.upper(), True
    return activity, False


class FrenchCompanyProvider:
    """At most four pages of 25 legal units; return local active establishments."""
    def __init__(self, http: PublicHttpClient, *, clock=utc_now):
        self.http, self.clock = http, clock

    def discover(self, query: SearchQuery) -> ProviderBatch:
        try:
            return self._discover(query)
        except (FetchError, ValidationError, KeyError, TypeError, ValueError) as exc:
            if isinstance(exc, ProviderError):
                raise
            raise ProviderError(f"French company provider failed: {getattr(exc, 'code', 'invalid_response')}") from exc

    def _discover(self, query):
        location_url = str(httpx.URL("https://geo.api.gouv.fr/communes", params={
            "nom": query.location, "fields": "nom,code,codesPostaux"}))
        communes = self.http.get_json(location_url)
        if not isinstance(communes, list):
            raise ProviderError("Invalid commune response")
        matches = [item for item in communes if match_text(item["nom"]) == match_text(query.location)]
        if len(matches) != 1:
            raise ProviderError("Location unknown or ambiguous; use the exact French commune name")
        commune = matches[0]
        postcodes = set(commune["codesPostaux"])
        if not postcodes or not all(re.fullmatch(r"\d{5}", code) for code in postcodes):
            raise ProviderError("Invalid commune postal codes")
        activity, is_code = activity_filter(query.activity)
        params = {"code_postal": ",".join(sorted(postcodes)), "etat_administratif": "A",
                  "minimal": "true", "include": "matching_etablissements,siege",
                  "per_page": "25", "limite_matching_etablissements": "100"}
        params["activite_principale" if is_code else "q"] = activity
        businesses, warnings = [], []
        if not is_code:
            warnings.append("Activity uses textual search, not a complete sector classification")
        collected = self.clock()
        for page in range(1, 5):
            url = str(httpx.URL("https://recherche-entreprises.api.gouv.fr/search",
                               params={**params, "page": str(page)}))
            payload = self.http.get_json(url)
            if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
                raise ProviderError("Invalid company search response")
            for company in payload["results"]:
                # Do not retain suppressed records or personal legal names from sole traders.
                if (company.get("statut_diffusion") != "O" or company.get("etat_administratif") != "A"
                        or not company.get("nature_juridique") or str(company["nature_juridique"]).startswith("1")):
                    warnings.append("Non-public, inactive or individual legal records excluded")
                    continue
                establishments = list(company.get("matching_etablissements") or [])
                if company.get("siege"):
                    establishments.append(company["siege"])
                for establishment in establishments:
                    city = match_text(establishment.get("libelle_commune"))
                    target = match_text(commune["nom"])
                    arrondissement = target in {"marseille", "lyon", "paris"} and bool(
                        re.fullmatch(re.escape(target) + r" \d+(?:er|e|eme)?(?: arrondissement)?", city))
                    if (establishment.get("code_postal") not in postcodes
                            or not (establishment.get("commune") == commune["code"] or city == target or arrondissement)
                            or establishment.get("etat_administratif") != "A"
                            or establishment.get("statut_diffusion_etablissement") != "O"
                            or is_code and establishment.get("activite_principale") != activity):
                        continue
                    source = SourceReference(source_name="API Recherche d'Entreprises / Sirene",
                                             source_url=url, collected_at=collected)
                    business = normalize_establishment(company, establishment, source)
                    # Keep the administrative location resolution as provenance too.
                    business.source_references.append(SourceReference(source_name="API Découpage administratif",
                                                                      source_url=location_url, collected_at=collected))
                    businesses.append(business)
            if len({b.internal_id for b in businesses}) >= query.limit:
                break
            total_pages = payload.get("total_pages")
            if not isinstance(total_pages, int) or total_pages < 0:
                raise ProviderError("Invalid company search pagination")
            if page >= total_pages:
                break
            if page == 4:
                warnings.append("Provider page budget reached; results are incomplete")
        warnings.append("Registry data does not establish whether an official website exists")
        return ProviderBatch(businesses=businesses, warnings=sorted(set(warnings)))


class FixtureProvider:
    def __init__(self, payload: dict):
        self.payload = payload

    def discover(self, query: SearchQuery) -> ProviderBatch:
        if (match_text(query.location) != "marseille" or
                activity_filter(query.activity) != ("45.20A", True)):
            raise ProviderError("Synthetic demo only supports garage automobile / Marseille")
        source = SourceReference(source_name="Synthetic fixture (not real businesses)",
                                 source_url="fixture:examples/discovery/companies.json",
                                 collected_at=datetime.fromisoformat("2026-10-08T00:00:00+00:00"))
        businesses = [normalize_establishment(company, establishment, source)
                      for company in self.payload["results"] for establishment in company["matching_etablissements"]]
        return ProviderBatch(businesses=businesses, warnings=["Synthetic demonstration: no real prospects or live measurements"])
