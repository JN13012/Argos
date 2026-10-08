"""Versioned contracts for discovery, provenance and qualification."""

from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha256
import json
from typing import Annotated, Literal, Protocol
from uuid import uuid4

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, JsonValue, field_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


Text = Annotated[str, Field(min_length=1, max_length=1000)]


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, allow_inf_nan=False)


class Opportunity(StrEnum):
    WEBSITE = "website"
    AI = "ai"
    CYBERSECURITY = "cybersecurity"


class SearchQuery(Model):
    activity: Text
    location: Text
    requested_opportunities: list[Opportunity] = Field(
        default_factory=lambda: list(Opportunity), min_length=1, max_length=3
    )
    limit: int = Field(default=20, ge=1, le=100)

    @field_validator("requested_opportunities")
    @classmethod
    def distinct_opportunities(cls, value):
        if len(value) != len(set(value)):
            raise ValueError("opportunities must be distinct")
        return value


class SourceReference(Model):
    source_name: Text
    source_url: Text
    collected_at: AwareDatetime


class SourceObservation(SourceReference):
    # The shared text cleanup must never alter raw evidence values.
    model_config = ConfigDict(str_strip_whitespace=False)
    id: Text
    field: Text
    raw_value: JsonValue
    value: JsonValue
    confidence: float = Field(ge=0, le=1)


def observation(source: SourceReference, field: str, raw: JsonValue,
                value: JsonValue, confidence: float = 0.95) -> SourceObservation:
    material = json.dumps([source.model_dump(mode="json"), field, raw, value],
                          sort_keys=True, ensure_ascii=False)
    return SourceObservation(**source.model_dump(), id=sha256(material.encode()).hexdigest()[:24],
                             field=field, raw_value=raw, value=value, confidence=confidence)


class ContactPolicy(Model):
    source: Text
    collected_at: AwareDatetime
    purpose: Literal["business_discovery_and_qualification"] = "business_discovery_and_qualification"
    contact_type: Literal["none", "public_business_contact"] = "none"
    deleted_at: AwareDatetime | None = None
    do_not_contact: bool = True


class Business(Model):
    internal_id: Text
    legal_name: Text
    trading_name: Text | None = None
    address: Text | None = None
    postal_code: str | None = Field(default=None, pattern=r"^\d{5}$")
    city: Text | None = None
    country: Literal["FR"] = "FR"
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    official_identifiers: dict[str, str] = Field(default_factory=dict)
    website: Text | None = None
    phone: Text | None = None
    professional_email: Text | None = None
    activity_code: Text | None = None
    source_references: list[SourceReference] = Field(default_factory=list)
    observations: list[SourceObservation] = Field(default_factory=list)
    contact_policy: ContactPolicy

    @field_validator("official_identifiers")
    @classmethod
    def valid_identifiers(cls, value):
        for key, identifier in value.items():
            length = {"siren": 9, "siret": 14}.get(key)
            if length is None or len(identifier) != length or not identifier.isascii() or not identifier.isdigit():
                raise ValueError("official identifiers must be SIREN (9 digits) or SIRET (14 digits)")
        if "siret" in value and "siren" in value and not value["siret"].startswith(value["siren"]):
            raise ValueError("SIRET must belong to SIREN")
        return value


class WebsiteHint(Model):
    siret: str = Field(pattern=r"^\d{14}$")
    website: Text
    source_url: Text
    collected_at: AwareDatetime
    official_association_declared: Literal[True]


class Signal(Model):
    name: Text
    value: JsonValue
    observation_ids: list[str] = Field(min_length=1)


class PageSummary(Model):
    url: Text
    status_code: int
    title: str | None = None
    response_ms: int = Field(ge=0)
    redirects: list[str] = Field(default_factory=list)


class EnrichmentRun(Model):
    id: str = Field(default_factory=lambda: str(uuid4()))
    collected_at: AwareDatetime
    status: Literal["no_website", "skipped", "ok", "partial", "inaccessible", "blocked"]
    pages: list[PageSummary] = Field(default_factory=list)
    observations: list[SourceObservation] = Field(default_factory=list)
    signals: list[Signal] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class ScoreReason(Model):
    signal: Text
    weight: int = Field(ge=0, le=100)
    evidence: Text
    observation_ids: list[str] = Field(min_length=1)


class Score(Model):
    value: int = Field(ge=0, le=100)
    interpretation: Text
    reasons: list[ScoreReason] = Field(default_factory=list)


class Scores(Model):
    website_opportunity_score: Score | None = None
    ai_automation_opportunity_score: Score | None = None
    cybersecurity_opportunity_score: Score | None = None
    data_confidence_score: Score


class Qualification(Model):
    business: Business
    enrichment: EnrichmentRun
    scores: Scores


class DiscoveryResult(Model):
    schema_version: Literal[1] = 1
    scoring_policy_version: Literal["conservative-v1"] = "conservative-v1"
    search_id: str = Field(default_factory=lambda: str(uuid4()))
    query: SearchQuery
    collected_at: AwareDatetime
    source_mode: Literal["official_api", "synthetic_demo"]
    qualifications: list[Qualification]
    warnings: list[str] = Field(default_factory=list)


class ProviderBatch(Model):
    businesses: list[Business]
    warnings: list[str] = Field(default_factory=list)


class DiscoveryProvider(Protocol):
    def discover(self, query: SearchQuery) -> ProviderBatch: ...


class QueryInterpreter(Protocol):
    """Future structured-query boundary; no LLM implementation or dependency."""
    def interpret(self, text: str) -> SearchQuery: ...


class ProviderError(ValueError):
    """Discovery failed; an empty successful search must not hide this error."""
