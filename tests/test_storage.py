import sqlite3
from collections.abc import Iterator
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pytest

from argos.osint import (
    Coverage,
    CoverageStatus,
    Entity,
    EntityType,
    Identifier,
    Observation,
    Search,
    SearchResult,
    SearchScope,
    SearchStatus,
)
from argos.osint.storage import SQLiteStorage

NOW = datetime(2026, 10, 10, 12, 0, 0, 123456, tzinfo=UTC)


@pytest.fixture
def storage(tmp_path: Path) -> Iterator[SQLiteStorage]:
    with SQLiteStorage(tmp_path / "argos.sqlite3") as database:
        yield database


@pytest.fixture
def entity() -> Entity:
    return Entity(uuid4(), EntityType.ESTABLISHMENT, "Garage d'Argos", NOW, NOW)


@pytest.fixture
def search() -> Search:
    return Search(
        uuid4(), SearchScope("garages", "Marseille"), "garages à Marseille",
        NOW, None, SearchStatus.RUNNING,
    )


@pytest.fixture
def coverage(search: Search) -> Coverage:
    return Coverage(
        search_id=search.id,
        connector="fixture",
        status=CoverageStatus.TRUNCATED,
        pages_processed=2,
        records_seen=10,
        entities_created=6,
        entities_reused=2,
        pagination_exhausted=False,
        truncated=True,
        exclusions={"hors périmètre": 2},
        errors=["Limite de la source atteinte"],
    )


def test_all_records_survive_database_reopening(
    tmp_path: Path, entity: Entity, search: Search, coverage: Coverage,
) -> None:
    path = tmp_path / ".argos" / "argos.sqlite3"
    identifier = Identifier(entity.id, "siret", "12345678900012", "fixture")
    observation = Observation(uuid4(), entity.id, "name", "Garage d'Argos", "fixture", NOW)
    result = SearchResult(search.id, entity.id, "fixture", NOW)

    with SQLiteStorage(path) as database:
        database.save_entity(entity)
        database.add_identifier(identifier)
        database.add_observation(observation)
        database.save_search(search)
        database.add_search_result(result)
        database.save_coverage(coverage)

    with SQLiteStorage(path) as reopened:
        assert reopened.get_entity(entity.id) == entity
        assert reopened.get_identifiers(entity.id) == [identifier]
        assert reopened.get_observations(entity.id) == [observation]
        assert reopened.get_search(search.id) == search
        assert reopened.get_search_results(search.id) == [result]
        restored = reopened.get_coverage(search.id, coverage.connector)
        assert restored == coverage
        assert restored is not None
        assert restored.status is CoverageStatus.TRUNCATED
        assert restored.truncated is True
        assert restored.pagination_exhausted is False


def test_entity_update_preserves_identity_creation_date_and_linked_records(
    storage: SQLiteStorage, entity: Entity,
) -> None:
    storage.save_entity(entity)
    identifier = Identifier(entity.id, "domain", "example.test", "fixture")
    observation = Observation(uuid4(), entity.id, "name", entity.display_name, "fixture", NOW)
    storage.add_identifier(identifier)
    storage.add_observation(observation)
    updated = replace(
        entity,
        display_name="Garage du Port – Marseille",
        created_at=NOW + timedelta(hours=1),
        updated_at=NOW + timedelta(hours=1),
    )

    storage.save_entity(updated)

    assert storage.get_entity(entity.id) == replace(updated, created_at=entity.created_at)
    assert storage.get_identifiers(entity.id) == [identifier]
    assert storage.get_observations(entity.id) == [observation]


@pytest.mark.parametrize("scheme", ["google_place_id", "siret"])
def test_identifiers_keep_provenance_without_duplicates(
    storage: SQLiteStorage, entity: Entity, scheme: str,
) -> None:
    storage.save_entity(entity)
    value = "12345678900012" if scheme == "siret" else "example-place-id"
    identifier = Identifier(entity.id, scheme, value, "first")
    other_source = replace(identifier, source="second")

    storage.add_identifier(identifier)
    storage.add_identifier(other_source)
    storage.add_identifier(identifier)

    assert storage.get_identifiers(entity.id) == [identifier, other_source]


@pytest.mark.parametrize("source", ["fixture", "sirene"])
def test_find_entity_by_siret(
    storage: SQLiteStorage, entity: Entity, source: str,
) -> None:
    storage.save_entity(entity)
    storage.add_identifier(Identifier(entity.id, "siret", "12345678900012", source))

    assert storage.find_entity_by_identifier("siret", "12345678900012") == entity
    assert storage.find_entity_by_identifier("siret", "12345678900013") is None
    assert storage.find_entity_by_identifier("siren", "12345678900012") is None


@pytest.mark.parametrize("source", ["sirene", "another_source"])
def test_same_siret_cannot_belong_to_two_entities(
    storage: SQLiteStorage, entity: Entity, source: str,
) -> None:
    other = replace(entity, id=uuid4(), display_name="Second établissement")
    storage.save_entity(entity)
    storage.save_entity(other)
    identifier = Identifier(entity.id, "siret", "12345678900012", "sirene")
    storage.add_identifier(identifier)

    with pytest.raises(sqlite3.IntegrityError, match="SIRET already belongs to another entity"):
        storage.add_identifier(replace(identifier, entity_id=other.id, source=source))

    assert storage.find_entity_by_identifier("siret", identifier.value) == entity
    assert storage.get_identifiers(entity.id) == [identifier]
    assert storage.get_identifiers(other.id) == []
    storage.add_identifier(replace(identifier, entity_id=other.id, value="12345678900013"))
    assert storage.find_entity_by_identifier("siret", "12345678900013") == other


def test_shared_siren_does_not_merge_establishments(
    storage: SQLiteStorage, entity: Entity,
) -> None:
    other = replace(entity, id=uuid4(), display_name="Second établissement")
    storage.save_entity(entity)
    storage.save_entity(other)
    first_id = Identifier(entity.id, "siren", "123456789", "fixture")
    second_id = replace(first_id, entity_id=other.id)

    storage.add_identifier(first_id)
    storage.add_identifier(second_id)

    assert storage.get_entity(entity.id) == entity
    assert storage.get_entity(other.id) == other
    assert storage.get_identifiers(entity.id) == [first_id]
    assert storage.get_identifiers(other.id) == [second_id]


def test_observations_preserve_conflicts_and_reject_overwrites(
    storage: SQLiteStorage, entity: Entity,
) -> None:
    storage.save_entity(entity)
    first = Observation(uuid4(), entity.id, "name", "Garage du Port", "first", NOW)
    second = replace(
        first, id=uuid4(), value="Garage de la Mer", source="second",
        observed_at=NOW + timedelta(hours=1),
    )
    storage.add_observation(second)
    storage.add_observation(first)

    with pytest.raises(sqlite3.IntegrityError):
        storage.add_observation(replace(first, value="Replacement"))

    assert storage.get_observations(entity.id) == [first, second]


def test_search_can_be_saved_then_completed(storage: SQLiteStorage, search: Search) -> None:
    storage.save_search(search)
    assert storage.get_search(search.id) == search
    completed = replace(
        search, status=SearchStatus.COMPLETED, completed_at=NOW + timedelta(minutes=5),
    )

    storage.save_search(completed)

    restored = storage.get_search(search.id)
    assert restored == completed
    assert restored is not None
    assert restored.status is SearchStatus.COMPLETED


def test_search_results_reuse_global_entities_and_preserve_each_source(
    storage: SQLiteStorage, entity: Entity, search: Search,
) -> None:
    other_search = replace(search, id=uuid4())
    storage.save_entity(entity)
    storage.save_search(search)
    storage.save_search(other_search)
    first = SearchResult(search.id, entity.id, "first", NOW)
    other_source = replace(first, connector="second", discovered_at=NOW + timedelta(minutes=1))
    other_result = replace(first, search_id=other_search.id)
    storage.add_search_result(first)
    storage.add_search_result(other_source)
    storage.add_search_result(other_result)
    storage.add_search_result(replace(first, discovered_at=NOW + timedelta(minutes=2)))
    updated = replace(entity, display_name="Updated global name", updated_at=NOW + timedelta(hours=1))
    storage.save_entity(updated)

    assert storage.get_search_results(search.id) == [first, other_source]
    assert storage.get_search_results(other_search.id) == [other_result]
    assert storage.get_entity(other_result.entity_id) == updated


def test_coverage_updates_are_isolated_by_search_and_source(
    storage: SQLiteStorage, search: Search, coverage: Coverage,
) -> None:
    other_search = replace(search, id=uuid4())
    storage.save_search(search)
    storage.save_search(other_search)
    other_source = replace(
        coverage, connector="other", status=CoverageStatus.FAILED,
        truncated=False, errors=["Source unavailable"],
    )
    other_report = replace(coverage, search_id=other_search.id)
    storage.save_coverage(coverage)
    storage.save_coverage(other_source)
    storage.save_coverage(other_report)
    completed = replace(
        coverage, status=CoverageStatus.COMPLETE_FOR_SOURCE, pages_processed=3,
        records_seen=12, entities_created=8, pagination_exhausted=True,
        truncated=False, errors=[],
    )

    storage.save_coverage(completed)

    assert storage.get_coverage(search.id, "fixture") == completed
    assert storage.get_coverage(search.id, "other") == other_source
    assert storage.get_coverage(other_search.id, "fixture") == other_report


def test_missing_records_return_none_or_empty_lists(storage: SQLiteStorage) -> None:
    unknown_id = uuid4()

    assert storage.get_entity(unknown_id) is None
    assert storage.get_search(unknown_id) is None
    assert storage.get_coverage(unknown_id, "fixture") is None
    assert storage.get_identifiers(unknown_id) == []
    assert storage.get_observations(unknown_id) == []
    assert storage.get_search_results(unknown_id) == []


def test_references_must_exist_and_failed_writes_leave_storage_usable(
    storage: SQLiteStorage, entity: Entity, search: Search, coverage: Coverage,
) -> None:
    storage.save_entity(entity)
    storage.save_search(search)
    missing_id = uuid4()

    with pytest.raises(sqlite3.IntegrityError):
        storage.add_identifier(Identifier(missing_id, "siret", "12345678900012", "fixture"))
    with pytest.raises(sqlite3.IntegrityError):
        storage.add_observation(Observation(uuid4(), missing_id, "name", "Unknown", "fixture", NOW))
    with pytest.raises(sqlite3.IntegrityError):
        storage.add_search_result(SearchResult(search.id, missing_id, "fixture", NOW))
    with pytest.raises(sqlite3.IntegrityError):
        storage.add_search_result(SearchResult(missing_id, entity.id, "fixture", NOW))
    with pytest.raises(sqlite3.IntegrityError):
        storage.save_coverage(replace(coverage, search_id=missing_id))

    result = SearchResult(search.id, entity.id, "fixture", NOW)
    storage.add_search_result(result)
    assert storage.get_search_results(search.id) == [result]
    assert storage.get_identifiers(entity.id) == []
    assert storage.get_observations(entity.id) == []
    assert storage.get_coverage(search.id, "fixture") is None


def test_mutated_models_are_validated_before_writing(
    storage: SQLiteStorage, entity: Entity,
) -> None:
    original = replace(entity)
    storage.save_entity(entity)
    entity.updated_at = NOW.replace(tzinfo=None)

    with pytest.raises(ValueError, match="updated_at.*UTC"):
        storage.save_entity(entity)

    assert storage.get_entity(entity.id) == original
