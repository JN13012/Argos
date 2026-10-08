"""Normalize selected public establishment fields without retaining personal records."""

from hashlib import sha256
import re
import unicodedata
from urllib.parse import urlsplit

from .models import Business, ContactPolicy, SourceReference, observation


def clean_text(value) -> str | None:
    if value is None:
        return None
    return " ".join(str(value).split()) or None


def match_text(value) -> str:
    text = unicodedata.normalize("NFKD", clean_text(value) or "")
    return " ".join("".join(c for c in text if not unicodedata.combining(c)).casefold().split())


def normalize_establishment(company: dict, establishment: dict,
                            source: SourceReference) -> Business:
    """Ignore directors, personal profiles and all unselected provider fields."""
    raw = {
        "legal_name": company.get("nom_raison_sociale") or company.get("nom_complet"),
        "trading_name": establishment.get("nom_commercial") or
                        next(iter(establishment.get("liste_enseignes") or []), None),
        "address": establishment.get("adresse"),
        "postal_code": establishment.get("code_postal"),
        "city": establishment.get("libelle_commune"),
        "latitude": establishment.get("latitude"),
        "longitude": establishment.get("longitude"),
        "activity_code": establishment.get("activite_principale") or company.get("activite_principale"),
    }
    values = {field: clean_text(value) for field, value in raw.items()}
    for field in ("latitude", "longitude"):
        values[field] = float(values[field]) if values[field] is not None else None
    identifiers = {key: clean_text(value) for key, value in
                   (("siren", company.get("siren")), ("siret", establishment.get("siret")))
                   if value is not None}
    identity = identifiers.get("siret") or repr(
        (identifiers.get("siren"), values["legal_name"], values["address"], values["postal_code"]))
    observations = [observation(source, field, raw[field], value)
                    for field, value in values.items() if value is not None]
    observations.extend(observation(source, f"official_identifiers.{key}", value, value)
                        for key, value in identifiers.items())
    observations.append(observation(source, "country", "French establishment", "FR"))
    return Business(**values, internal_id=sha256(identity.encode()).hexdigest()[:24],
                    official_identifiers=identifiers, observations=observations,
                    source_references=[source],
                    contact_policy=ContactPolicy(source=source.source_name, collected_at=source.collected_at))


def website_domain(website: str | None) -> str | None:
    try:
        host = urlsplit(website or "").hostname
        return host.casefold().removeprefix("www.") if host else None
    except ValueError:
        return None


def _identity_key(business: Business):
    return (match_text(business.legal_name), match_text(business.address), business.postal_code)


def _relationship(left: Business, right: Business) -> str | None:
    a, b = left.official_identifiers, right.official_identifiers
    if a.get("siret") and b.get("siret"):
        return "merge" if a["siret"] == b["siret"] else None
    if a.get("siren") and b.get("siren"):
        if a["siren"] != b["siren"]:
            return None
        # SIREN identifies a company, not a branch. Missing branch data is ambiguous.
        if not a.get("siret") and not b.get("siret") and _identity_key(left) == _identity_key(right):
            return "merge"
        return "ambiguous"
    same_domain = website_domain(left.website) and website_domain(left.website) == website_domain(right.website)
    same_address = left.address and right.address and _identity_key(left) == _identity_key(right)
    if same_address:
        return "merge"
    return "ambiguous" if same_domain else None


def deduplicate(businesses: list[Business]) -> tuple[list[Business], list[str]]:
    results, warnings = [], []
    for business in businesses:
        for existing in results:
            relationship = _relationship(existing, business)
            if relationship == "ambiguous":
                warnings.append(f"Ambiguous identity retained separately: {existing.internal_id} / {business.internal_id}")
            if relationship != "merge":
                continue
            known = {item.id for item in existing.observations}
            existing.observations.extend(item for item in business.observations if item.id not in known)
            for reference in business.source_references:
                if reference not in existing.source_references:
                    existing.source_references.append(reference)
            for field in ("legal_name", "trading_name", "address", "postal_code", "city", "country",
                          "latitude", "longitude", "website", "phone", "professional_email", "activity_code"):
                old, new = getattr(existing, field), getattr(business, field)
                if old is None:
                    setattr(existing, field, new)
                elif new is not None and old != new:
                    warnings.append(f"Conflicting {field} for {existing.internal_id}; first value retained with both observations")
            existing.official_identifiers.update(business.official_identifiers)
            existing.contact_policy.do_not_contact |= business.contact_policy.do_not_contact
            if business.contact_policy.deleted_at:
                existing.contact_policy.deleted_at = business.contact_policy.deleted_at
            break
        else:
            results.append(business.model_copy(deep=True))
    return results, sorted(set(warnings))


def normalize_phone(raw: str) -> str | None:
    raw = re.sub(r"[\s().-]", "", raw)
    if re.fullmatch(r"0[1-9]\d{8}", raw):
        return "+33" + raw[1:]
    return raw if re.fullmatch(r"\+33[1-9]\d{8}", raw) else None
