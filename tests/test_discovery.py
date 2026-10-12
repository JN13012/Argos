import json
from collections.abc import Iterator
from copy import deepcopy
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from unittest.mock import Mock
from uuid import uuid4

import pytest

from argos.osint.connectors import SireneConnector
from argos.osint.discovery import DiscoveryEngine
from argos.osint.models import (
    CoverageStatus,
    Entity,
    EntityType,
    Identifier,
    Observation,
    SearchScope,
    SearchStatus,
)
from argos.osint.storage import SQLiteStorage

SCOPE = SearchScope("garage automobile", "Marseille")
QUERY = (
    "periode(activitePrincipaleEtablissement:45.20A) AND codeCommuneEtablissement:13055"
)


@pytest.fixture
def storage(tmp_path: Path) -> Iterator[SQLiteStorage]:
    with SQLiteStorage(tmp_path / "argos.sqlite3") as database:
        yield database


@pytest.fixture
def connector() -> Mock:
    return Mock(spec=SireneConnector)


@pytest.fixture
def establishment() -> dict[str, Any]:
    return {
        "siret": "12345678900012",
        "siren": "123456789",
        "uniteLegale": {"denominationUniteLegale": "Garage d'Argos"},
        "adresseEtablissement": {
            "numeroVoieEtablissement": "12",
            "typeVoieEtablissement": "RUE",
            "libelleVoieEtablissement": "DU PORT",
            "codePostalEtablissement": "13001",
            "libelleCommuneEtablissement": "MARSEILLE",
            "complementAdresseEtablissement": None,
        },
        "periodesEtablissement": [
            {
                "dateFin": "2020-12-31",
                "activitePrincipaleEtablissement": "45.20B",
                "etatAdministratifEtablissement": "F",
                "enseigne1Etablissement": "Old name",
            },
            {
                "dateFin": None,
                "activitePrincipaleEtablissement": "45.20A",
                "etatAdministratifEtablissement": "A",
                "enseigne1Etablissement": "Garage du Port",
            },
        ],
    }


def page(
    records: list[dict[str, Any]],
    cursor: str = "*",
    next_cursor: str = "*",
) -> dict[str, Any]:
    return {
        "header": {"statut": 200, "curseur": cursor, "curseurSuivant": next_cursor},
        "etablissements": records,
    }


def test_new_establishment_persists_search_identity_observations_and_coverage(
    tmp_path: Path,
    connector: Mock,
    establishment: dict[str, Any],
) -> None:
    path = tmp_path / "argos.sqlite3"
    connector.search_establishments.return_value = page([establishment])
    with SQLiteStorage(path) as storage:
        search = DiscoveryEngine(storage, connector).discover_sirene(SCOPE, QUERY)

    with SQLiteStorage(path) as storage:
        assert storage.get_search(search.id) == search
        assert search.scope == SCOPE
        assert search.query == QUERY
        assert search.status is SearchStatus.COMPLETED
        assert search.completed_at is not None
        assert search.completed_at >= search.started_at
        assert search.started_at.utcoffset() == timedelta(0)
        entity = storage.find_entity_by_identifier("siret", establishment["siret"])
        assert entity is not None
        assert entity.entity_type is EntityType.ESTABLISHMENT
        assert entity.display_name == "Garage d'Argos"
        assert search.started_at <= entity.created_at <= search.completed_at
        assert storage.get_identifiers(entity.id) == [
            Identifier(entity.id, "siren", "123456789", "sirene"),
            Identifier(entity.id, "siret", "12345678900012", "sirene"),
        ]
        observations = storage.get_observations(entity.id)
        values = {observation.field: observation.value for observation in observations}
        assert values["name"] == "Garage d'Argos"
        assert values["activity"] == "45.20A"
        assert values["administrative_status"] == "A"
        assert json.loads(values["address"]) == {
            key: value
            for key, value in establishment["adresseEtablissement"].items()
            if value is not None
        }
        assert all(observation.source == "sirene" for observation in observations)
        assert all(
            search.started_at <= item.observed_at <= search.completed_at
            for item in observations
        )
        results = storage.get_search_results(search.id)
        assert len(results) == 1
        assert results[0].entity_id == entity.id
        assert results[0].connector == "sirene"
        coverage = storage.get_coverage(search.id, "sirene")
        assert coverage is not None
        assert (coverage.entities_created, coverage.entities_reused) == (1, 0)
        assert (coverage.pages_processed, coverage.records_seen) == (1, 1)
        assert coverage.status is CoverageStatus.COMPLETE_FOR_SOURCE
        assert coverage.pagination_exhausted and not coverage.truncated
        assert coverage.errors == []
    connector.search_establishments.assert_called_once_with(query=QUERY, cursor="*")


def test_existing_siret_reuses_entity_and_preserves_observation_history(
    storage: SQLiteStorage,
    connector: Mock,
    establishment: dict[str, Any],
) -> None:
    old_time = datetime(2026, 1, 1, tzinfo=UTC)
    entity = Entity(
        uuid4(), EntityType.ESTABLISHMENT, "Original name", old_time, old_time
    )
    storage.save_entity(entity)
    identifier = Identifier(
        entity.id, "siret", establishment["siret"], "another_source"
    )
    storage.add_identifier(identifier)
    previous = Observation(
        uuid4(), entity.id, "administrative_status", "F", "sirene", old_time
    )
    storage.add_observation(previous)
    connector.search_establishments.return_value = page([establishment])
    engine = DiscoveryEngine(storage, connector)

    first = engine.discover_sirene(SCOPE, QUERY)
    second = engine.discover_sirene(SCOPE, QUERY)

    restored = storage.find_entity_by_identifier("siret", establishment["siret"])
    assert restored is not None
    assert restored.id == entity.id
    assert restored.created_at == old_time
    assert restored.updated_at > old_time
    assert restored.display_name == "Garage d'Argos"
    assert identifier in storage.get_identifiers(entity.id)
    for search in (first, second):
        coverage = storage.get_coverage(search.id, "sirene")
        assert coverage is not None
        assert (coverage.entities_created, coverage.entities_reused) == (0, 1)
        assert [
            result.entity_id for result in storage.get_search_results(search.id)
        ] == [entity.id]
    observations = storage.get_observations(entity.id)
    assert previous in observations
    assert sorted(
        item.value for item in observations if item.field == "administrative_status"
    ) == [
        "A",
        "A",
        "F",
    ]


def test_shared_siren_does_not_merge_different_sirets(
    storage: SQLiteStorage,
    connector: Mock,
    establishment: dict[str, Any],
) -> None:
    second = {**establishment, "siret": "12345678900013"}
    connector.search_establishments.return_value = page([establishment, second])

    search = DiscoveryEngine(storage, connector).discover_sirene(SCOPE, QUERY)

    first_entity = storage.find_entity_by_identifier("siret", establishment["siret"])
    second_entity = storage.find_entity_by_identifier("siret", second["siret"])
    assert first_entity is not None and second_entity is not None
    assert first_entity.id != second_entity.id
    for entity in (first_entity, second_entity):
        assert Identifier(
            entity.id, "siren", "123456789", "sirene"
        ) in storage.get_identifiers(entity.id)
    coverage = storage.get_coverage(search.id, "sirene")
    assert coverage is not None
    assert (coverage.entities_created, coverage.entities_reused) == (2, 0)


def test_multiple_pages_continue_until_cursor_is_exhausted(
    storage: SQLiteStorage,
    connector: Mock,
    establishment: dict[str, Any],
) -> None:
    connector.search_establishments.side_effect = [
        page([establishment], next_cursor="next+/="),
        page([], cursor="next+/=", next_cursor="next+/="),
    ]

    search = DiscoveryEngine(storage, connector).discover_sirene(
        SCOPE, QUERY, max_pages=2
    )

    connector.search_establishments.assert_called_with(query=QUERY, cursor="next+/=")
    assert connector.search_establishments.call_count == 2
    coverage = storage.get_coverage(search.id, "sirene")
    assert coverage is not None
    assert (coverage.pages_processed, coverage.records_seen) == (2, 1)
    assert coverage.pagination_exhausted and not coverage.truncated
    assert coverage.status is CoverageStatus.COMPLETE_FOR_SOURCE
    assert search.status is SearchStatus.COMPLETED


def test_max_pages_records_truncated_coverage(
    storage: SQLiteStorage,
    connector: Mock,
    establishment: dict[str, Any],
) -> None:
    connector.search_establishments.return_value = page(
        [establishment], next_cursor="next"
    )

    search = DiscoveryEngine(storage, connector).discover_sirene(
        SCOPE, QUERY, max_pages=1
    )

    assert connector.search_establishments.call_count == 1
    coverage = storage.get_coverage(search.id, "sirene")
    assert coverage is not None
    assert coverage.status is CoverageStatus.TRUNCATED
    assert coverage.truncated and not coverage.pagination_exhausted
    assert coverage.pages_processed == 1
    assert coverage.errors == []
    assert search.status is SearchStatus.PARTIAL
    assert search.completed_at is not None


@pytest.mark.parametrize("useful_results", [False, True])
def test_connector_error_finalizes_failed_or_partial_search(
    storage: SQLiteStorage,
    connector: Mock,
    establishment: dict[str, Any],
    useful_results: bool,
) -> None:
    connector.search_establishments.side_effect = (
        [page([establishment], next_cursor="next"), RuntimeError("Sirene unavailable")]
        if useful_results
        else RuntimeError("Sirene unavailable")
    )

    search = DiscoveryEngine(storage, connector).discover_sirene(SCOPE, QUERY)

    coverage = storage.get_coverage(search.id, "sirene")
    assert coverage is not None
    assert coverage.status is (
        CoverageStatus.PARTIAL if useful_results else CoverageStatus.FAILED
    )
    assert search.status is (
        SearchStatus.PARTIAL if useful_results else SearchStatus.FAILED
    )
    assert search.completed_at is not None
    assert storage.get_search(search.id) == search
    assert coverage.errors == ["RuntimeError: Sirene unavailable"]
    assert (coverage.pages_processed, coverage.records_seen) == (
        (1, 1) if useful_results else (0, 0)
    )
    assert len(storage.get_search_results(search.id)) == int(useful_results)
    assert not coverage.pagination_exhausted and not coverage.truncated


def test_empty_exhausted_search_completes_without_entities(
    storage: SQLiteStorage, connector: Mock
) -> None:
    connector.search_establishments.return_value = page([])

    search = DiscoveryEngine(storage, connector).discover_sirene(SCOPE, QUERY)

    coverage = storage.get_coverage(search.id, "sirene")
    assert coverage is not None
    assert coverage.status is CoverageStatus.COMPLETE_FOR_SOURCE
    assert (
        coverage.records_seen,
        coverage.entities_created,
        coverage.entities_reused,
    ) == (0, 0, 0)
    assert coverage.pagination_exhausted
    assert storage.get_search_results(search.id) == []
    assert search.status is SearchStatus.COMPLETED


@pytest.mark.parametrize("name_source", ["enseigne", "usual", "person", "siret"])
def test_name_fallbacks_and_absent_facts_create_no_placeholder_observations(
    storage: SQLiteStorage,
    connector: Mock,
    name_source: str,
) -> None:
    record: dict[str, Any] = {
        "siret": "12345678900012",
        "uniteLegale": {},
        "adresseEtablissement": {"codePostalEtablissement": None},
        "periodesEtablissement": [{"dateFin": None}],
    }
    if name_source == "enseigne":
        record["periodesEtablissement"][0]["enseigne1Etablissement"] = "Garage du Port"
    elif name_source == "usual":
        record["periodesEtablissement"][0]["denominationUsuelleEtablissement"] = (
            "Garage du Port"
        )
    elif name_source == "person":
        record["uniteLegale"] = {
            "prenomUsuelUniteLegale": "Jean",
            "nomUniteLegale": "Dupont",
        }
    connector.search_establishments.return_value = page([record])

    search = DiscoveryEngine(storage, connector).discover_sirene(SCOPE, QUERY)

    entity = storage.find_entity_by_identifier("siret", record["siret"])
    assert entity is not None
    expected = {"person": "Jean Dupont", "siret": record["siret"]}.get(
        name_source, "Garage du Port"
    )
    assert entity.display_name == expected
    assert storage.get_identifiers(entity.id) == [
        Identifier(entity.id, "siret", record["siret"], "sirene")
    ]
    assert [item.field for item in storage.get_observations(entity.id)] == (
        [] if name_source == "siret" else ["name"]
    )
    assert search.status is SearchStatus.COMPLETED


def test_missing_siret_does_not_create_an_entity(
    storage: SQLiteStorage,
    connector: Mock,
    establishment: dict[str, Any],
) -> None:
    invalid = deepcopy(establishment)
    del invalid["siret"]
    connector.search_establishments.return_value = page([invalid])

    search = DiscoveryEngine(storage, connector).discover_sirene(SCOPE, QUERY)

    coverage = storage.get_coverage(search.id, "sirene")
    assert coverage is not None
    assert coverage.status is CoverageStatus.FAILED
    assert coverage.entities_created == 0
    assert coverage.errors == ["ValueError: Sirene establishment is missing its SIRET"]
    assert storage.get_search_results(search.id) == []


def test_missing_cursor_does_not_claim_complete_coverage(
    storage: SQLiteStorage,
    connector: Mock,
    establishment: dict[str, Any],
) -> None:
    connector.search_establishments.return_value = {
        "header": {},
        "etablissements": [establishment],
    }

    search = DiscoveryEngine(storage, connector).discover_sirene(SCOPE, QUERY)

    coverage = storage.get_coverage(search.id, "sirene")
    assert coverage is not None
    assert coverage.status is CoverageStatus.PARTIAL
    assert not coverage.pagination_exhausted
    assert coverage.errors == [
        "ValueError: Sirene response is missing a pagination cursor"
    ]


def test_invalid_page_limit_fails_before_calling_connector(
    storage: SQLiteStorage, connector: Mock
) -> None:
    with pytest.raises(ValueError, match="max_pages must be positive"):
        DiscoveryEngine(storage, connector).discover_sirene(SCOPE, QUERY, max_pages=0)
    connector.search_establishments.assert_not_called()
