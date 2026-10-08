"""The query -> discovery -> enrichment -> normalization -> scoring -> result path."""

from .enrichment import WebEnricher
from .models import (DiscoveryProvider, DiscoveryResult, Qualification, SearchQuery,
                     SourceReference, WebsiteHint, observation, utc_now)
from .normalize import deduplicate
from .scoring import score_business


class DiscoveryService:
    def __init__(self, provider: DiscoveryProvider, enricher: WebEnricher, *, clock=utc_now):
        self.provider, self.enricher, self.clock = provider, enricher, clock

    def run(self, query: SearchQuery, *, hints: list[WebsiteHint] = (), skip_web=False,
            source_mode="official_api") -> DiscoveryResult:
        batch = self.provider.discover(query)
        if len({hint.siret for hint in hints}) != len(hints):
            raise ValueError("Website hints must have distinct SIRETs")
        by_siret = {hint.siret: hint for hint in hints}
        for business in batch.businesses:
            hint = by_siret.get(business.official_identifiers.get("siret"))
            if hint:
                source = SourceReference(source_name="User-declared official website association",
                                         source_url=hint.source_url, collected_at=hint.collected_at)
                business.website = hint.website
                business.source_references.append(source)
                business.observations.append(observation(source, "website", hint.website, hint.website, 0.6))
        businesses, warnings = deduplicate(batch.businesses)
        result = DiscoveryResult(query=query, collected_at=self.clock(), source_mode=source_mode,
                                 qualifications=[], warnings=sorted(set(batch.warnings + warnings)))
        if len(businesses) > query.limit:
            result.warnings.append("Result limit reached; remaining establishments were omitted")
        for business in businesses[:query.limit]:
            run = self.enricher.enrich(business, skip=skip_web)
            for field in ("phone", "professional_email"):
                matching = [item for item in run.observations if item.field == field and item.value]
                if matching:
                    setattr(business, field, matching[0].value[0])
                    item = matching[0]
                    business.observations.append(observation(
                        SourceReference(source_name=item.source_name, source_url=item.source_url,
                                        collected_at=item.collected_at), field, item.raw_value,
                        getattr(business, field), item.confidence))
                    business.contact_policy.contact_type = "public_business_contact"
                    business.contact_policy.source = item.source_name
                    business.contact_policy.collected_at = item.collected_at
            for item in run.observations:
                reference = SourceReference(source_name=item.source_name, source_url=item.source_url,
                                            collected_at=item.collected_at)
                if reference not in business.source_references:
                    business.source_references.append(reference)
            result.qualifications.append(Qualification(business=business, enrichment=run,
                                                        scores=score_business(business, run, query.requested_opportunities)))
        return result
