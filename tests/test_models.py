from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone
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

NOW = datetime(2026, 10, 10, 12, tzinfo=UTC)


@pytest.fixture
def entity() -> Entity:
    return Entity(
        id=uuid4(),
        entity_type=EntityType.ESTABLISHMENT,
        display_name="Garage du Port",
        created_at=NOW,
        updated_at=NOW,
    )


@pytest.fixture
def identifier(entity: Entity) -> Identifier:
    return Identifier(
        entity_id=entity.id,
        scheme="siret",
        value="12345678900012",
        source="fixture",
    )


@pytest.fixture
def observation(entity: Entity) -> Observation:
    return Observation(
        id=uuid4(),
        entity_id=entity.id,
        field="display_name",
        value="Garage du Port",
        source="fixture",
        observed_at=NOW,
    )


@pytest.fixture
def search() -> Search:
    return Search(
        id=uuid4(),
        scope=SearchScope(activity="garages", location="Marseille"),
        query="garages à Marseille",
        started_at=NOW,
        completed_at=None,
        status=SearchStatus.PENDING,
    )


@pytest.fixture
def search_result(search: Search, entity: Entity) -> SearchResult:
    return SearchResult(
        search_id=search.id,
        entity_id=entity.id,
        connector="fixture",
        discovered_at=NOW,
    )


@pytest.fixture
def coverage(search: Search) -> Coverage:
    return Coverage(
        search_id=search.id,
        connector="fixture",
        status=CoverageStatus.COMPLETE_FOR_SOURCE,
        pages_processed=2,
        records_seen=20,
        entities_created=12,
        entities_reused=8,
        pagination_exhausted=True,
        truncated=False,
    )


@pytest.fixture(params=[
    datetime(2026, 10, 10, 12),
    datetime(2026, 10, 10, 12, tzinfo=timezone(timedelta(hours=1))),
], ids=["naive", "non-utc"])
def invalid_datetime(request: pytest.FixtureRequest) -> datetime:
    return request.param


def test_scope_strips_surrounding_whitespace() -> None:
    scope = SearchScope(activity="  garages\t", location=" Marseille ")

    assert scope.activity == "garages"
    assert scope.location == "Marseille"


@pytest.mark.parametrize("name", ["activity", "location"])
@pytest.mark.parametrize("value", ["", " \t\n"])
def test_scope_rejects_blank_fields(name: str, value: str) -> None:
    scope = SearchScope(activity="garages", location="Marseille")

    with pytest.raises(ValueError, match=name):
        replace(scope, **{name: value})


@pytest.mark.parametrize(("attribute", "value"), [
    ("activity", "car washes"),
    ("location", "Paris"),
])
def test_scope_is_immutable(attribute: str, value: str) -> None:
    scope = SearchScope(activity="garages", location="Marseille")

    with pytest.raises(FrozenInstanceError):
        setattr(scope, attribute, value)


def test_entity_exists_without_external_identifiers(entity: Entity) -> None:
    assert entity.entity_type is EntityType.ESTABLISHMENT
    assert entity.entity_type.value == "establishment"
    assert entity.display_name == "Garage du Port"

    entity.display_name = "Garage du Vieux Port"

    assert entity.display_name == "Garage du Vieux Port"


@pytest.mark.parametrize("value", ["", " \t"])
def test_entity_rejects_blank_display_name(entity: Entity, value: str) -> None:
    with pytest.raises(ValueError, match="display_name"):
        replace(entity, display_name=value)


@pytest.mark.parametrize("name", ["created_at", "updated_at"])
def test_entity_requires_utc_timestamps(
    entity: Entity, name: str, invalid_datetime: datetime,
) -> None:
    with pytest.raises(ValueError, match=f"{name}.*UTC"):
        replace(entity, **{name: invalid_datetime})


@pytest.mark.parametrize(("scheme", "value"), [
    ("siret", "12345678900012"),
    ("google_place_id", "example-place-id"),
])
def test_identifier_supports_multiple_sources(
    entity: Entity, scheme: str, value: str,
) -> None:
    identifier = Identifier(entity.id, scheme, value, "fixture")

    assert identifier.entity_id == entity.id
    assert identifier.scheme == scheme
    assert identifier.value == value
    assert identifier.source == "fixture"


@pytest.mark.parametrize("name", ["scheme", "value", "source"])
@pytest.mark.parametrize("value", ["", " \t"])
def test_identifier_rejects_blank_fields(
    identifier: Identifier, name: str, value: str,
) -> None:
    with pytest.raises(ValueError, match=name):
        replace(identifier, **{name: value})


def test_observation_has_a_utc_timestamp(observation: Observation) -> None:
    assert observation.observed_at.tzinfo is UTC
    assert observation.observed_at.utcoffset() == timedelta(0)


def test_conflicting_observations_remain_separate(observation: Observation) -> None:
    newer = replace(
        observation,
        id=uuid4(),
        value="Garage du Vieux Port",
        source="another_fixture",
        observed_at=NOW + timedelta(hours=1),
    )

    assert newer.entity_id == observation.entity_id
    assert newer.field == observation.field
    assert newer.id != observation.id
    assert observation.value == "Garage du Port"
    assert observation.source == "fixture"
    assert newer.value == "Garage du Vieux Port"
    assert newer.source == "another_fixture"


@pytest.mark.parametrize(("attribute", "value"), [
    ("value", "Updated name"),
    ("source", "another_fixture"),
])
def test_observation_is_immutable(
    observation: Observation, attribute: str, value: str,
) -> None:
    with pytest.raises(FrozenInstanceError):
        setattr(observation, attribute, value)


def test_observation_preserves_raw_values(observation: Observation) -> None:
    assert replace(observation, value="  raw value  ").value == "  raw value  "
    assert replace(observation, value="").value == ""


def test_observation_requires_utc(
    observation: Observation, invalid_datetime: datetime,
) -> None:
    with pytest.raises(ValueError, match="observed_at.*UTC"):
        replace(observation, observed_at=invalid_datetime)


@pytest.mark.parametrize("name", ["field", "source"])
@pytest.mark.parametrize("value", ["", " \t"])
def test_observation_rejects_blank_provenance(
    observation: Observation, name: str, value: str,
) -> None:
    with pytest.raises(ValueError, match=name):
        replace(observation, **{name: value})


@pytest.mark.parametrize("status", list(SearchStatus))
def test_search_represents_each_status(search: Search, status: SearchStatus) -> None:
    assert replace(search, status=status).status is status


def test_search_can_be_unfinished(search: Search) -> None:
    assert search.status is SearchStatus.PENDING
    assert search.completed_at is None


def test_search_can_be_completed(search: Search) -> None:
    completed_at = NOW + timedelta(minutes=5)
    completed = replace(
        search, status=SearchStatus.COMPLETED, completed_at=completed_at,
    )

    assert completed.completed_at == completed_at
    assert completed.status is SearchStatus.COMPLETED


@pytest.mark.parametrize("name", ["started_at", "completed_at"])
def test_search_requires_utc_timestamps(
    search: Search, name: str, invalid_datetime: datetime,
) -> None:
    with pytest.raises(ValueError, match=f"{name}.*UTC"):
        replace(search, **{name: invalid_datetime})


@pytest.mark.parametrize("value", ["", " \t"])
def test_search_rejects_blank_query(search: Search, value: str) -> None:
    with pytest.raises(ValueError, match="query"):
        replace(search, query=value)


def test_search_result_references_search_and_global_entity(
    search_result: SearchResult, search: Search, entity: Entity,
) -> None:
    another_search = replace(search, id=uuid4())
    another_result = replace(search_result, search_id=another_search.id)

    assert search_result.search_id == search.id
    assert another_result.search_id == another_search.id
    assert search_result.entity_id == another_result.entity_id == entity.id
    entity.display_name = "Updated name"
    assert search_result.entity_id == entity.id


def test_search_result_requires_utc(
    search_result: SearchResult, invalid_datetime: datetime,
) -> None:
    with pytest.raises(ValueError, match="discovered_at.*UTC"):
        replace(search_result, discovered_at=invalid_datetime)


@pytest.mark.parametrize("value", ["", " \t"])
def test_search_result_rejects_blank_connector(
    search_result: SearchResult, value: str,
) -> None:
    with pytest.raises(ValueError, match="connector"):
        replace(search_result, connector=value)


@pytest.mark.parametrize("status", list(CoverageStatus))
def test_coverage_represents_each_status(
    coverage: Coverage, status: CoverageStatus,
) -> None:
    report = replace(
        coverage,
        status=status,
        pagination_exhausted=status is CoverageStatus.COMPLETE_FOR_SOURCE,
        truncated=status is CoverageStatus.TRUNCATED,
        errors=["Source unavailable"] if status is CoverageStatus.FAILED else [],
    )

    assert report.status is status
    assert report.pagination_exhausted is (status is CoverageStatus.COMPLETE_FOR_SOURCE)
    assert report.truncated is (status is CoverageStatus.TRUNCATED)
    if status is CoverageStatus.FAILED:
        assert report.errors == ["Source unavailable"]


def test_coverage_collections_are_not_shared(coverage: Coverage) -> None:
    other = Coverage(
        search_id=coverage.search_id,
        connector="another_fixture",
        status=CoverageStatus.PARTIAL,
        pages_processed=0,
        records_seen=0,
        entities_created=0,
        entities_reused=0,
        pagination_exhausted=False,
        truncated=False,
    )

    coverage.exclusions["outside_scope"] = 2
    coverage.errors.append("Source unavailable")

    assert other.exclusions == {}
    assert other.errors == []


@pytest.mark.parametrize("name", [
    "pages_processed", "records_seen", "entities_created", "entities_reused",
])
def test_coverage_rejects_negative_counters(coverage: Coverage, name: str) -> None:
    with pytest.raises(ValueError, match=name):
        replace(coverage, **{name: -1})


def test_coverage_rejects_negative_exclusion_counts(coverage: Coverage) -> None:
    with pytest.raises(ValueError, match="exclusion"):
        replace(coverage, exclusions={"outside_scope": -1})


@pytest.mark.parametrize("value", ["", " \t"])
def test_coverage_rejects_blank_connector(coverage: Coverage, value: str) -> None:
    with pytest.raises(ValueError, match="connector"):
        replace(coverage, connector=value)
