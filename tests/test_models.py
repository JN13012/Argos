from dataclasses import replace
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


def test_entity_exists_without_external_identifiers(entity: Entity) -> None:
    assert entity.display_name == "Garage du Port"


def test_entity_rejects_blank_display_name(entity: Entity) -> None:
    with pytest.raises(ValueError, match="display_name"):
        replace(entity, display_name="")


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
def test_identifier_supports_multiple_schemes(
    entity: Entity, scheme: str, value: str,
) -> None:
    identifier = Identifier(entity.id, scheme, value, "fixture")

    assert identifier.entity_id == entity.id
    assert identifier.scheme == scheme
    assert identifier.value == value


@pytest.mark.parametrize("name", ["scheme", "value", "source"])
def test_identifier_rejects_blank_fields(
    identifier: Identifier, name: str,
) -> None:
    with pytest.raises(ValueError, match=name):
        replace(identifier, **{name: ""})


def test_conflicting_observations_remain_separate(observation: Observation) -> None:
    newer = Observation(
        id=uuid4(),
        entity_id=observation.entity_id,
        field=observation.field,
        value="Garage du Vieux Port",
        source="another_fixture",
        observed_at=NOW + timedelta(hours=1),
    )

    observations = [observation, newer]
    assert [(fact.value, fact.source) for fact in observations] == [
        ("Garage du Port", "fixture"),
        ("Garage du Vieux Port", "another_fixture"),
    ]


def test_observation_requires_utc(
    observation: Observation, invalid_datetime: datetime,
) -> None:
    with pytest.raises(ValueError, match="observed_at.*UTC"):
        replace(observation, observed_at=invalid_datetime)


@pytest.mark.parametrize("name", ["field", "source"])
def test_observation_rejects_blank_provenance(
    observation: Observation, name: str,
) -> None:
    with pytest.raises(ValueError, match=name):
        replace(observation, **{name: ""})


def test_search_can_be_unfinished(search: Search) -> None:
    assert search.completed_at is None


@pytest.mark.parametrize("name", ["started_at", "completed_at"])
def test_search_requires_utc_timestamps(
    search: Search, name: str, invalid_datetime: datetime,
) -> None:
    with pytest.raises(ValueError, match=f"{name}.*UTC"):
        replace(search, **{name: invalid_datetime})


def test_search_rejects_blank_query(search: Search) -> None:
    with pytest.raises(ValueError, match="query"):
        replace(search, query="")


def test_search_result_references_search_and_global_entity(
    search_result: SearchResult, search: Search, entity: Entity,
) -> None:
    another_search = replace(search, id=uuid4())
    another_result = replace(search_result, search_id=another_search.id)

    assert search_result.search_id == search.id
    assert another_result.search_id == another_search.id
    assert search_result.entity_id == another_result.entity_id == entity.id


def test_search_result_requires_utc(
    search_result: SearchResult, invalid_datetime: datetime,
) -> None:
    with pytest.raises(ValueError, match="discovered_at.*UTC"):
        replace(search_result, discovered_at=invalid_datetime)


def test_search_result_rejects_blank_connector(search_result: SearchResult) -> None:
    with pytest.raises(ValueError, match="connector"):
        replace(search_result, connector="")


def test_coverage_can_report_an_exhausted_source(coverage: Coverage) -> None:
    assert coverage.status is CoverageStatus.COMPLETE_FOR_SOURCE
    assert coverage.pagination_exhausted
    assert not coverage.truncated


def test_coverage_can_report_truncation(coverage: Coverage) -> None:
    report = replace(
        coverage,
        status=CoverageStatus.TRUNCATED,
        pagination_exhausted=False,
        truncated=True,
    )

    assert report.truncated
    assert not report.pagination_exhausted


def test_coverage_preserves_source_errors(coverage: Coverage) -> None:
    report = replace(
        coverage,
        status=CoverageStatus.FAILED,
        pagination_exhausted=False,
        errors=["Source unavailable"],
    )

    assert report.errors == ["Source unavailable"]
    assert not report.pagination_exhausted


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


def test_coverage_rejects_blank_connector(coverage: Coverage) -> None:
    with pytest.raises(ValueError, match="connector"):
        replace(coverage, connector="")
