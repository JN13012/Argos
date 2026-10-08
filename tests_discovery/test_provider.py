import json

import httpx
import pytest

from argos.discovery.models import ProviderError, SearchQuery
from argos.discovery.providers import FrenchCompanyProvider
from conftest import COLLECTED, response


def company(siren="000000001", city="MARSEILLE", postal="13001"):
    item = {"siret": siren + "00001", "adresse": "LOCAL ADDRESS", "code_postal": postal,
            "libelle_commune": city, "commune": "13201", "etat_administratif": "A",
            "statut_diffusion_etablissement": "O", "activite_principale": "45.20A"}
    return {"siren": siren, "nom_raison_sociale": "Local Garage", "nature_juridique": "5499",
            "statut_diffusion": "O", "etat_administratif": "A", "activite_principale": "45.20A",
            "siege": {**item, "siret": siren + "00002", "code_postal": "75001", "libelle_commune": "PARIS"},
            "matching_etablissements": [item], "dirigeants": [{"nom": "Do not retain"}]}


def provider(http_factory, payload=None, *, status=200, communes=None, requests=None):
    def handler(request):
        if requests is not None:
            requests.append(request)
        if request.headers["host"] == "geo.api.gouv.fr":
            # geo.api.gouv.fr returns no matches for the unsupported type=commune.
            if request.url.params.get("type") == "commune":
                return response("[]", headers={"content-type": "application/json"})
            return response(json.dumps(communes if communes is not None else [
                {"nom": "Marseillette", "code": "11220", "codesPostaux": ["11800"]},
                {"nom": "Marseille", "code": "13055", "codesPostaux": ["13001", "13002"]}]),
                headers={"content-type": "application/json"})
        return response(json.dumps(payload if payload is not None else {"results": [company()], "total_pages": 1}),
                        status=status, headers={"content-type": "application/json"})
    return FrenchCompanyProvider(http_factory(handler), clock=lambda: COLLECTED)


def query(**kwargs):
    return SearchQuery(**{**{"activity": "garage automobile", "location": "Marseille"}, **kwargs})


def test_local_establishment_not_distant_headquarters(http_factory):
    requests = []
    batch = provider(http_factory, requests=requests).discover(query())
    assert len(batch.businesses) == 1
    business = batch.businesses[0]
    assert business.postal_code == "13001"
    assert business.address == "LOCAL ADDRESS"
    assert business.official_identifiers["siret"] == "00000000100001"
    assert business.website is None
    assert "Do not retain" not in business.model_dump_json()
    params = requests[1].url.params
    assert params["activite_principale"] == "45.20A"
    assert params["minimal"] == "true"
    assert "dirigeants" not in params["include"]
    assert params["code_postal"] == "13001,13002"
    assert business.observations[0].collected_at == COLLECTED
    assert "recherche-entreprises.api.gouv.fr" in business.observations[0].source_url


@pytest.mark.parametrize("change", ["suppressed_company", "individual", "inactive", "suppressed_establishment",
                                   "wrong_city", "wrong_establishment_activity"])
def test_unsuitable_records_excluded(change, http_factory):
    item = company()
    if change == "suppressed_company":
        item["statut_diffusion"] = "P"
    elif change == "individual":
        item["nature_juridique"] = "1000"
    elif change == "inactive":
        item["etat_administratif"] = "C"
    elif change == "suppressed_establishment":
        item["matching_etablissements"][0]["statut_diffusion_etablissement"] = "P"
    elif change == "wrong_city":
        item["matching_etablissements"][0].update(commune="99999", libelle_commune="Other commune")
    else:
        item["matching_etablissements"][0]["activite_principale"] = "99.99Z"
    assert provider(http_factory, {"results": [item], "total_pages": 1}).discover(query()).businesses == []


@pytest.mark.parametrize("status", [429, 500, 403])
def test_provider_http_failures_are_not_empty_success(status, http_factory):
    with pytest.raises(ProviderError, match=f"http_status_{status}"):
        provider(http_factory, status=status).discover(query())


@pytest.mark.parametrize("payload", [{}, {"results": "bad"}, {"results": [company()], "total_pages": "many"}])
def test_provider_malformed_response(payload, http_factory):
    with pytest.raises(ProviderError):
        provider(http_factory, payload).discover(query())


def test_unknown_and_ambiguous_location_fail(http_factory):
    for communes in ([], [{"nom": "Marseille", "code": "13055", "codesPostaux": ["13001"]}] * 2):
        with pytest.raises(ProviderError, match="unknown or ambiguous"):
            provider(http_factory, communes=communes).discover(query())


def test_provider_pagination_stops_after_four_pages(http_factory):
    requests = []
    batch = provider(http_factory, {"results": [company()], "total_pages": 20}, requests=requests).discover(query(limit=20))
    assert len(requests) == 5  # one location request and four search pages
    assert any("page budget" in warning for warning in batch.warnings)


def test_provider_network_error_is_useful(http_factory):
    def fail(request):
        raise httpx.ConnectError("Network unavailable", request=request)
    with pytest.raises(ProviderError, match="http_error"):
        FrenchCompanyProvider(http_factory(fail)).discover(query())
