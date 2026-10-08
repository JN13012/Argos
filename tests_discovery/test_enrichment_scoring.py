import httpx
import pytest
import ssl

from argos.discovery.enrichment import WebEnricher, parse_html
from argos.discovery.models import Opportunity
from argos.discovery.scoring import score_business
from conftest import COLLECTED, response


def enricher(http_factory, *, robots="User-agent: *\nAllow: /", html=None, pages=None, calls=None):
    def handler(request):
        path = request.url.path
        if calls is not None:
            calls.append(path)
        if path == "/robots.txt":
            if robots == "unavailable":
                return response(status=503)
            return response(robots, headers={"content-type": "text/plain"})
        if path == "/" and html is not None:
            return response(html)
        if pages and path in pages:
            return response(pages[path])
        raise httpx.ConnectError("Unavailable", request=request)
    return WebEnricher(http_factory(handler), clock=lambda: COLLECTED, sleep=lambda _s: None)


def test_absent_site_is_low_confidence_not_proven_absence(business, http_factory):
    calls = []
    run = enricher(http_factory, calls=calls).enrich(business)
    scores = score_business(business, run, list(Opportunity))
    assert run.status == "no_website"
    assert calls == []
    assert scores.website_opportunity_score.value == 25
    assert "does not prove" in scores.website_opportunity_score.reasons[0].evidence
    assert scores.ai_automation_opportunity_score.value == 0
    assert scores.cybersecurity_opportunity_score.value == 0
    assert scores.data_confidence_score.value < 50


def test_inaccessible_site_does_not_invent_missing_features(business, http_factory):
    business.website = "https://external.example/"
    run = enricher(http_factory).enrich(business)
    assert run.status == "inaccessible"
    assert run.errors == ["http_error"]
    scores = score_business(business, run, list(Opportunity))
    assert scores.website_opportunity_score.value == scores.cybersecurity_opportunity_score.value == 0
    assert not scores.website_opportunity_score.reasons


@pytest.mark.parametrize("robots", ["User-agent: *\nDisallow: /", "unavailable",
                                   "User-agent: *\nCrawl-delay: 20"])
def test_robots_blocks_homepage(business, robots, http_factory):
    business.website = "https://external.example/"
    calls = []
    run = enricher(http_factory, robots=robots, html="<html></html>", calls=calls).enrich(business)
    assert run.status == "blocked"
    assert calls == ["/robots.txt"]
    assert "robots_disallowed" in run.errors


def test_internal_pages_only_and_no_social_requests(business, http_factory):
    business.website = "http://external.example/"
    html = """<html><title>Garage</title><body>Horaires et services
      <a href='/contact'>Contact</a><a href='/services'>Services</a><a href='/about'>About</a>
      <a href='http://other.example/contact'>Contact elsewhere</a>
      <a href='https://linkedin.com/company/example'>Public social link</a>
      <a href='mailto:contact@external.example'>Business contact</a>
      <a href='mailto:person.name@external.example'>Personal contact</a>
      <a href='tel:0400000000'>Phone</a></body></html>"""
    calls = []
    run = enricher(http_factory, html=html, pages={"/contact": "<html>Contact</html>",
                                                   "/services": "<html>Services</html>"}, calls=calls).enrich(business)
    assert run.status == "ok"
    assert calls == ["/robots.txt", "/", "/contact", "/services"]
    assert len(run.pages) == 3
    assert "person.name" not in run.model_dump_json()
    assert any(item.field == "public_social_links" and item.value for item in run.observations)
    scores = score_business(business, run, list(Opportunity))
    assert scores.website_opportunity_score.value == 55
    assert scores.ai_automation_opportunity_score.value == 40
    assert scores.cybersecurity_opportunity_score.value == 10
    assert "not a vulnerability" in scores.cybersecurity_opportunity_score.interpretation
    assert score_business(business, run, list(Opportunity)) == scores
    ids = {item.id for item in business.observations + run.observations}
    for score in scores.model_dump().values():
        if score:
            assert 0 <= score["value"] <= 100
            for reason in score["reasons"]:
                assert set(reason["observation_ids"]) <= ids


def test_booking_on_internal_page_suppresses_absence_factor(business, http_factory):
    business.website = "https://external.example/"
    run = enricher(http_factory, html="<html><a href='/contact'>Contact</a></html>",
                   pages={"/contact": "<html><a href='https://booking.example/'>Réserver</a></html>"}).enrich(business)
    assert next(s.value for s in run.signals if s.name == "online_booking_link_detected") is True
    assert score_business(business, run, list(Opportunity)).ai_automation_opportunity_score.value == 0


def test_internal_failure_does_not_claim_booking_absence(business, http_factory):
    business.website = "https://external.example/"
    run = enricher(http_factory, html="<html><a href='/contact'>Contact</a></html>").enrich(business)
    assert run.status == "partial"
    assert next(s.value for s in run.signals if s.name == "online_booking_link_detected") is None
    assert score_business(business, run, list(Opportunity)).ai_automation_opportunity_score.value == 0


def test_robots_is_checked_after_https_redirect(business, http_factory):
    business.website = "http://external.example/"
    calls = []
    def handler(request):
        calls.append((request.url.scheme, request.url.path))
        if request.url.path == "/robots.txt":
            return response("User-agent: *\nDisallow: /" if request.url.scheme == "https" else "User-agent: *\nAllow: /")
        return response(status=301, headers={"location": "https://external.example/"})
    run = WebEnricher(http_factory(handler), sleep=lambda _s: None).enrich(business)
    assert run.status == "blocked"
    assert calls == [("http", "/robots.txt"), ("http", "/"), ("https", "/robots.txt")]


def test_only_requested_scores_are_computed(business, http_factory):
    run = enricher(http_factory).enrich(business)
    scores = score_business(business, run, [Opportunity.WEBSITE])
    assert scores.website_opportunity_score is not None
    assert scores.ai_automation_opportunity_score is None
    assert scores.cybersecurity_opportunity_score is None
    assert scores.data_confidence_score is not None


def test_certificate_failure_has_small_explained_cyber_opportunity(business, http_factory):
    business.website = "https://external.example/"
    def handler(request):
        if request.url.path == "/robots.txt":
            return response(status=404)
        raise httpx.ConnectError("TLS", request=request) from ssl.SSLCertVerificationError("Untrusted certificate")
    run = WebEnricher(http_factory(handler)).enrich(business)
    scores = score_business(business, run, list(Opportunity))
    assert run.status == "inaccessible"
    assert scores.cybersecurity_opportunity_score.value == 15
    assert scores.cybersecurity_opportunity_score.reasons[0].signal == "tls_certificate_invalid"
    assert scores.website_opportunity_score.value == 0


def test_contact_links_do_not_store_message_bodies_or_tracking_queries():
    fields, _links = parse_html(b"""<html><a href='mailto:contact@external.example?body=private-data'>Contact</a>
        <a href='https://facebook.com/public-company?tracking=secret'>Social</a></html>""", "https://external.example/")
    assert fields["generic_email_links"] == ["mailto:contact@external.example"]
    assert fields["public_social_links"] == ["https://facebook.com/public-company"]
    assert "private-data" not in repr(fields)
    assert "secret" not in repr(fields)


def test_visible_markup_only_and_no_script_execution():
    fields, links = parse_html(b"""<html><head><meta name='generator' content='WordPress 123'>
        <meta name='description' content='Business description'></head>
        <body><script>throw Error('reservation services');</script><p>Garage</p>
        <a href='/contact?delete=true'>Contact</a></body></html>""", "https://external.example/")
    assert fields["online_booking_link_detected"] is False
    assert fields["hours_or_services_text_detected"] is False
    assert fields["public_technologies"] == ["WordPress"]
    assert fields["meta_description"] == "Business description"
    assert links == []
