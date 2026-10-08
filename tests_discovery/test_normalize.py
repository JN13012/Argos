import pytest
from pydantic import ValidationError

from argos.discovery.models import SearchQuery, SourceReference, observation
from argos.discovery.normalize import deduplicate, normalize_establishment, normalize_phone
from conftest import COLLECTED


def test_normalization_preserves_raw_and_normalized_value_and_ignores_people():
    company = {"siren": "000000001", "nom_raison_sociale": "  Garage   Exemple ",
               "dirigeants": [{"nom": "Private person", "date_de_naissance": "1900-01-01"}]}
    establishment = {"siret": "00000000100001", "adresse": " 1  RUE FICTIVE ", "code_postal": "13001",
                     "libelle_commune": "MARSEILLE", "latitude": "43.29", "longitude": "5.37"}
    source = SourceReference(source_name="Synthetic", source_url="fixture:company", collected_at=COLLECTED)
    item = normalize_establishment(company, establishment, source)
    assert item.legal_name == "Garage Exemple"
    assert item.latitude == 43.29
    obs = next(o for o in item.observations if o.field == "legal_name")
    assert obs.raw_value == "  Garage   Exemple "
    assert obs.value == item.legal_name
    assert obs.source_url == source.source_url
    assert obs.collected_at == COLLECTED
    assert "Private person" not in item.model_dump_json()


def test_same_siret_merges_and_preserves_conflicting_observations(business):
    other = business.model_copy(deep=True)
    other.legal_name = "Changed legal name"
    source = SourceReference(source_name="Other source", source_url="fixture:other", collected_at=COLLECTED)
    other.observations = [observation(source, "legal_name", other.legal_name, other.legal_name)]
    result, warnings = deduplicate([business, other])
    assert len(result) == 1
    assert result[0].legal_name == business.legal_name
    assert other.observations[0] in result[0].observations
    assert any("Conflicting legal_name" in item for item in warnings)
    assert business.observations != result[0].observations  # original objects were preserved


def test_same_siren_different_siret_is_separate(business):
    other = business.model_copy(deep=True)
    other.internal_id = "different"
    other.official_identifiers["siret"] = "00000010200002"
    assert len(deduplicate([business, other])[0]) == 2


def test_domain_collision_is_ambiguous_not_merged(business):
    other = business.model_copy(deep=True)
    business.official_identifiers = {}
    other.official_identifiers = {}
    business.website, other.website = "https://shared.example/", "https://www.shared.example/"
    other.address, other.legal_name, other.internal_id = "OTHER ADDRESS", "Other company", "other"
    result, warnings = deduplicate([business, other])
    assert len(result) == 2
    assert any("Ambiguous" in item for item in warnings)


def test_identical_name_address_fallback_merges(business):
    other = business.model_copy(deep=True)
    business.official_identifiers, other.official_identifiers = {}, {}
    other.legal_name = "GARAGE DÉMO CLASSIQUE"
    assert len(deduplicate([business, other])[0]) == 1


def test_missing_siret_with_same_siren_is_ambiguous(business):
    other = business.model_copy(deep=True)
    other.official_identifiers.pop("siret")
    result, warnings = deduplicate([business, other])
    assert len(result) == 2
    assert warnings


def test_missing_branch_identifiers_do_not_reuse_internal_id():
    source = SourceReference(source_name="Synthetic", source_url="fixture:test", collected_at=COLLECTED)
    company = {"siren": "000000001", "nom_raison_sociale": "Garage"}
    first = normalize_establishment(company, {"adresse": "First address"}, source)
    second = normalize_establishment(company, {"adresse": "Second address"}, source)
    result, warnings = deduplicate([first, second])
    assert len(result) == 2
    assert len({item.internal_id for item in result}) == 2
    assert warnings


@pytest.mark.parametrize("raw,expected", [("04 00 00 00 00", "+33400000000"),
                                           ("+33 (4) 00.00.00.00", "+33400000000"), ("bad", None)])
def test_phone(raw, expected):
    assert normalize_phone(raw) == expected


@pytest.mark.parametrize("changes", [{"activity": " "}, {"limit": 0}, {"limit": 101},
                                     {"requested_opportunities": ["website", "website"]},
                                     {"requested_opportunities": ["invalid"]}])
def test_query_rejects_invalid_inputs(changes):
    with pytest.raises(ValidationError):
        SearchQuery(**{**{"activity": "garage automobile", "location": "Marseille"}, **changes})


def test_nonfinite_coordinate_and_inconsistent_identifiers_rejected(business):
    for changes in ({"latitude": float("nan")}, {"official_identifiers": {"siret": "123", "siren": "000000001"}},
                    {"official_identifiers": {"siret": "00000000200001", "siren": "000000001"}}):
        with pytest.raises(ValidationError):
            type(business).model_validate({**business.model_dump(), **changes})
