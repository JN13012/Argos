"""Read visible site metadata with a small page budget and fail-closed robots policy."""

import re
import time
from hashlib import sha256
from urllib.parse import unquote, urljoin, urlsplit
from urllib.robotparser import RobotFileParser

from selectolax.parser import HTMLParser

from .http import FetchError, PublicHttpClient, RequestBudget, validated_url
from .models import Business, EnrichmentRun, PageSummary, Signal, SourceReference, observation, utc_now
from .normalize import match_text, normalize_phone


GENERIC_MAILBOXES = {"contact", "info", "accueil", "garage", "atelier", "service", "services",
                    "secretariat", "reservation", "reservations", "rdv", "devis", "commercial"}
SOCIAL_HOSTS = {"facebook.com", "instagram.com", "linkedin.com", "youtube.com", "x.com"}
PAGE_PATH = re.compile(r"(?:contact|a-propos|about|reservation|rendez-vous|services|rdv)", re.I)


def site_hosts(website: str) -> set[str]:
    host = validated_url(website).host
    bare = host.removeprefix("www.")
    return {bare, "www." + bare}


def parse_html(body: bytes, url: str) -> tuple[dict, list[str]]:
    tree = HTMLParser(body)
    title = tree.css_first("title")
    description = tree.css_first('meta[name="description" i]')
    viewport = tree.css_first('meta[name="viewport" i]')
    generator = tree.css_first('meta[name="generator" i]')
    technologies = []
    if generator and "wordpress" in generator.attributes.get("content", "").lower():
        technologies.append("WordPress")
    if tree.css('[src*="wp-content"], [href*="wp-content"]') and "WordPress" not in technologies:
        technologies.append("WordPress")
    for node in tree.css("script, style, noscript"):
        node.decompose()
    text = match_text(tree.body.text(separator=" ") if tree.body else tree.text(separator=" "))
    links, phones, emails, socials, phone_links, email_links = [], [], [], [], [], []
    booking = False
    for link in tree.css("a[href]"):
        href = link.attributes.get("href", "").strip()
        if href.lower().startswith("tel:"):
            phone = normalize_phone(unquote(href[4:]).split("?")[0])
            if phone:
                phones.append(phone)
                phone_links.append(href.split("?")[0])
            continue
        if href.lower().startswith("mailto:"):
            email = unquote(href[7:]).split("?")[0].lower()
            if (re.fullmatch(r"[a-z0-9._+-]+@[a-z0-9.-]+\.[a-z]{2,}", email)
                    and email.split("@")[0] in GENERIC_MAILBOXES):
                emails.append(email)
                email_links.append(href.split("?")[0])
            continue
        target = urljoin(url, href)
        try:
            parts = urlsplit(target)
            host = (parts.hostname or "").removeprefix("www.").lower()
        except ValueError:
            continue
        if parts.scheme not in {"http", "https"}:
            continue
        if host in SOCIAL_HOSTS:
            socials.append(parts._replace(query="", fragment="").geturl())
        label = match_text(link.text(separator=" "))
        if re.search(r"(?:reserv(?:er|ation)|rendez-vous|rendez vous|booking|prendre rdv)", label + " " + parts.path):
            booking = True
        if not parts.query and PAGE_PATH.search(parts.path) and not re.search(
                r"\.(?:pdf|zip|jpg|png|exe)$", parts.path, re.I):
            links.append(target.split("#")[0])
    forms = any(form.css('textarea, input[type="email" i]') for form in tree.css("form"))
    return {
        "title": title.text(strip=True)[:500] if title else None,
        "meta_description": description.attributes.get("content", "")[:1000] if description else None,
        "meta_description_present": bool(description and description.attributes.get("content", "").strip()),
        "mobile_viewport_present": bool(viewport and viewport.attributes.get("content", "").strip()),
        "contact_form_detected": forms,
        "online_booking_link_detected": booking,
        "phone": sorted(set(phones)),
        "professional_email": sorted(set(emails)),
        "public_phone_links": sorted(set(phone_links)),
        "generic_email_links": sorted(set(email_links)),
        "public_social_links": sorted(set(socials))[:10],
        "public_technologies": technologies,
        "hours_or_services_text_detected": bool(re.search(r"(?:horaires|ouverture|vidange|revision|pneus|services)", text)),
    }, list(dict.fromkeys(links))


class WebEnricher:
    def __init__(self, http: PublicHttpClient, *, max_pages: int = 3, clock=utc_now, sleep=time.sleep):
        if not 1 <= max_pages <= 3:
            raise ValueError("page budget must be between one and three")
        self.http, self.max_pages, self.clock, self.sleep = http, max_pages, clock, sleep

    def enrich(self, business: Business, *, skip=False) -> EnrichmentRun:
        collected = self.clock()
        if business.website is None or skip:
            source = SourceReference(source_name="Discovery qualification", source_url=f"business:{business.internal_id}",
                                     collected_at=collected)
            item = observation(source, "website_identified", business.website, business.website is not None, 0.4)
            return EnrichmentRun(collected_at=collected, status="skipped" if skip else "no_website",
                                 observations=[item], signals=[Signal(name="website_identified", value=item.value,
                                                                    observation_ids=[item.id])])
        run = EnrichmentRun(collected_at=collected, status="ok")
        try:
            hosts = site_hosts(business.website)
            start = str(validated_url(business.website))
        except FetchError as exc:
            run.status, run.errors = "blocked", [exc.code]
            return run
        robots_cache = {}
        last_request = {}
        budget = RequestBudget()

        def permitted(url):
            parsed = validated_url(url)
            origin = str(parsed.copy_with(path="/", query=None, fragment=None))
            if origin not in robots_cache:
                try:
                    page = self.http.get(urljoin(origin, "robots.txt"), allowed_hosts=hosts, budget=budget)
                    source = SourceReference(source_name="Public website robots policy", source_url=page.url,
                                             collected_at=collected)
                    run.observations.append(observation(source, "robots_http_status", page.status_code, page.status_code, 0.9))
                    if page.status_code == 404:
                        rules = None
                    elif page.status_code == 200:
                        rules = RobotFileParser()
                        rules.parse(page.body.decode("utf-8", errors="replace").splitlines())
                    else:
                        raise FetchError(f"robots_http_status_{page.status_code}")
                    robots_cache[origin] = rules
                except FetchError as exc:
                    run.errors.append("robots:" + exc.code)
                    robots_cache[origin] = False
            rules = robots_cache[origin]
            if rules is False:
                return False
            delay = 0
            if rules is not None:
                if not rules.can_fetch("ArgosDiscovery", url):
                    return False
                delay = rules.crawl_delay("ArgosDiscovery") or 0
                rate = rules.request_rate("ArgosDiscovery")
                if rate:
                    delay = max(delay, rate.seconds / rate.requests)
                if delay > 5:
                    run.errors.append("robots:crawl_delay_exceeds_local_budget")
                    return False
            wait = max(0, max(delay, 0.2) - (time.monotonic() - last_request.get(origin, 0)))
            if wait:
                self.sleep(wait)
            last_request[origin] = time.monotonic()
            return True

        pending, seen, parsed_fields = [start], set(), []
        while pending and len(seen) < self.max_pages:
            url = pending.pop(0)
            if url in seen:
                continue
            seen.add(url)
            try:
                page = self.http.get(url, allowed_hosts=hosts, permit=permitted, budget=budget)
                seen.add(page.url)
                source = SourceReference(source_name="Public website (passive HTML)",
                                         source_url=page.url, collected_at=collected)
                metadata = {"http_status": page.status_code, "final_url": page.url,
                            "redirects": page.redirects, "response_ms": page.response_ms,
                            "https_verified": page.url.startswith("https://"),
                            "content_sha256": sha256(page.body).hexdigest(),
                            "public_server_header": page.headers.get("server", "")[:200] or None,
                            "public_powered_by_header": page.headers.get("x-powered-by", "")[:200] or None}
                for field, value in metadata.items():
                    run.observations.append(observation(source, field, value, value, 0.9))
                run.pages.append(PageSummary(url=page.url, status_code=page.status_code,
                                             response_ms=page.response_ms, redirects=page.redirects))
                if not 200 <= page.status_code < 300:
                    raise FetchError(f"http_status_{page.status_code}")
                content_type = page.headers.get("content-type", "").lower()
                if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
                    raise FetchError("non_html_response")
                fields, links = parse_html(page.body, page.url)
                run.pages[-1].title = fields["title"]
                parsed_fields.append(fields)
                for field, value in fields.items():
                    raw_field = {"phone": "public_phone_links", "professional_email": "generic_email_links"}.get(field, field)
                    run.observations.append(observation(source, field, fields[raw_field], value, 0.7))
                for target in links:
                    try:
                        checked = validated_url(target)
                        if checked.host in hosts and target not in seen and target not in pending:
                            pending.append(target)
                    except FetchError:
                        continue
            except FetchError as exc:
                run.errors.append(exc.code)
                source = SourceReference(source_name="Public website request", source_url=url, collected_at=collected)
                run.observations.append(observation(source, "fetch_error", exc.code, exc.code, 0.9))
                if exc.code == "tls_certificate_invalid":
                    item = observation(source, "tls_certificate_invalid", True, True, 0.9)
                    run.observations.append(item)
                    run.signals.append(Signal(name=item.field, value=True, observation_ids=[item.id]))
                if not parsed_fields:
                    run.status = "blocked" if exc.code in {"robots_disallowed", "redirect_outside_domain",
                                                           "non_public_address", "non_public_host", "invalid_url"} else "inaccessible"
                    break
                run.status = "partial"
        if parsed_fields:
            self._signals(run, parsed_fields)
        return run

    @staticmethod
    def _signals(run, fields):
        first = fields[0]
        selected = {
            "meta_description_present": first["meta_description_present"],
            "mobile_viewport_present": first["mobile_viewport_present"],
            "contact_form_detected": any(f["contact_form_detected"] for f in fields),
            "online_booking_link_detected": True if any(f["online_booking_link_detected"] for f in fields)
                                            else False if run.status == "ok" else None,
            "public_business_contact_detected": any(f["phone"] or f["professional_email"] for f in fields),
            "hours_or_services_text_detected": any(f["hours_or_services_text_detected"] for f in fields),
        }
        for name, value in selected.items():
            observation_fields = {"phone", "professional_email"} if name == "public_business_contact_detected" else {name}
            ids = [item.id for item in run.observations if item.field in observation_fields]
            run.signals.append(Signal(name=name, value=value, observation_ids=ids))
        homepage_url = run.pages[0].url
        ids = [item.id for item in run.observations if item.field == "final_url" and item.source_url == homepage_url]
        run.signals.append(Signal(name="page_served_over_http", value=homepage_url.startswith("http://"),
                                  observation_ids=ids))
