"""Conservative, deterministic potential-opportunity scores; never vulnerability ratings."""

from .models import Business, EnrichmentRun, Opportunity, Score, ScoreReason, Scores


def score_business(business: Business, run: EnrichmentRun, requested: list[Opportunity]) -> Scores:
    signals = {item.name: item for item in run.signals}
    observations = business.observations + run.observations
    website, ai, cyber, confidence = [], [], [], []

    def add(reasons, signal_name, weight, explanation):
        signal = signals.get(signal_name)
        if signal is not None:
            reasons.append(ScoreReason(signal=signal_name, weight=weight, evidence=explanation,
                                       observation_ids=signal.observation_ids))

    def value(name):
        item = signals.get(name)
        return item.value if item else None

    if value("website_identified") is False:
        add(website, "website_identified", 25,
            "No website identified in the available sources; this does not prove that no website exists.")
    if run.status in {"ok", "partial"}:
        if value("page_served_over_http") is True:
            add(website, "page_served_over_http", 15, "The observed homepage was served over HTTP; HTTPS availability was not tested.")
            add(cyber, "page_served_over_http", 10, "Observed HTTP page: potential cybersecurity service opportunity, not a vulnerability finding.")
        for name, weight, label in (("mobile_viewport_present", 15, "mobile viewport"),
                                    ("meta_description_present", 10, "meta description")):
            if value(name) is False:
                add(website, name, weight, f"No {label} found in the fetched homepage HTML.")
        if value("contact_form_detected") is False and value("public_business_contact_detected") is False:
            add(website, "contact_form_detected", 10, "No contact form or generic business contact detected on the fetched pages.")
        appointment_activity = business.activity_code == "45.20A"
        if appointment_activity and value("online_booking_link_detected") is False:
            add(website, "online_booking_link_detected", 15, "No booking link detected in this limited crawl; manually verify.")
            add(ai, "online_booking_link_detected", 20, "Automotive servicing can use appointments; no booking link detected in fetched HTML.")
            if value("public_business_contact_detected") is True:
                add(ai, "public_business_contact_detected", 10, "A public contact channel is visible while no booking link was detected; workflow remains unknown.")
            if value("hours_or_services_text_detected") is True:
                add(ai, "hours_or_services_text_detected", 10, "Visible hours/services text may support simple information automation; demand is unverified.")
    if value("tls_certificate_invalid") is True:
        add(cyber, "tls_certificate_invalid", 15, "TLS certificate verification failed; configuration and commercial relevance need human review.")

    for field, weight, label in (("legal_name", 10, "Source-backed identity"),
                                 ("official_identifiers.siret", 15, "Source-backed establishment identifier"),
                                 ("address", 10, "Source-backed address"), ("city", 5, "Source-backed locality"),
                                 ("activity_code", 5, "Source-backed activity"), ("website", 10, "Declared website association")):
        matching = [item for item in business.observations if item.field == field and item.value is not None]
        if matching:
            confidence.append(ScoreReason(signal=field, weight=round(weight * max(item.confidence for item in matching)),
                                          evidence=label + "; confidence reflects source and coverage, not commercial demand.",
                                          observation_ids=[item.id for item in matching]))
    if run.status in {"ok", "partial"}:
        ids = [item.id for item in run.observations if item.field == "http_status"]
        confidence.append(ScoreReason(signal="html_coverage", weight=20 if run.status == "ok" else 10,
                                      evidence="Limited public HTML coverage; JavaScript and hidden workflows are unknown.",
                                      observation_ids=ids))

    def make(reasons, interpretation):
        return Score(value=min(100, sum(item.weight for item in reasons)), reasons=reasons,
                     interpretation=interpretation)

    known_ids = {item.id for item in observations}
    assert all(set(reason.observation_ids) <= known_ids for reason in website + ai + cyber + confidence)
    return Scores(
        website_opportunity_score=make(website, "Potential website service opportunity; manual qualification required")
        if Opportunity.WEBSITE in requested else None,
        ai_automation_opportunity_score=make(ai, "Potential AI/automation service opportunity; manual qualification required")
        if Opportunity.AI in requested else None,
        cybersecurity_opportunity_score=make(cyber, "Potential cybersecurity service opportunity; not a vulnerability rating")
        if Opportunity.CYBERSECURITY in requested else None,
        data_confidence_score=make(confidence, "Observation provenance and coverage; independent of opportunity scores"),
    )
