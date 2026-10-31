"""Readable reports generated from saved searches without calling the API."""

import html
import json
import re
import unicodedata
from pathlib import Path
from zoneinfo import ZoneInfo

from .models import Coverage, CoverageStatus, Search
from .storage import SQLiteStorage


def format_address(value: str) -> str:
    """Render stored address JSON as a postal address."""
    try:
        address = json.loads(value)
    except ValueError:
        return value
    if not isinstance(address, dict):
        return value
    parts = []
    for keys in (
        ("complementAdresseEtablissement",),
        (
            "numeroVoieEtablissement",
            "indiceRepetitionEtablissement",
            "typeVoieEtablissement",
            "libelleVoieEtablissement",
        ),
        ("distributionSpecialeEtablissement",),
        (
            "codePostalEtablissement",
            "libelleCommuneEtablissement",
            "libelleCommuneEtrangerEtablissement",
        ),
        ("libellePaysEtrangerEtablissement",),
    ):
        part = " ".join(str(address[key]) for key in keys if address.get(key))
        if part:
            parts.append(part)
    return ", ".join(parts) or value


def _safe(value: object) -> str:
    text = html.escape(str(value)).replace("\r", " ").replace("\n", " ")
    for character in ("\\", "`", "*", "_", "[", "]", "|", "#"):
        text = text.replace(character, "\\" + character)
    return text


def _slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")[:100].rstrip("-")
    if not slug:
        raise ValueError("Report name must contain letters or digits")
    return slug


def _report_directory(output_dir: str | Path, search: Search, name: str | None) -> Path:
    source = Path(output_dir) / "sirene"
    if name is not None:
        return source / _slug(name)
    # Reuse an existing named group when exporting the same search or scope.
    identity = f"- **Identifiant de recherche :** {search.id}"
    scope = f"**Recherche :** {_safe(search.scope.activity)} — {_safe(search.scope.location)}"
    existing = []
    for report in sorted(source.glob("*/rapport-*.md")):
        lines = report.read_text(encoding="utf-8").splitlines()
        if identity in lines:
            return report.parent
        if scope in lines:
            existing.append(report.parent)
    if existing:
        return existing[0]
    return source / _slug(f"{search.scope.activity}-{search.scope.location}")


def _save_numbered_report(directory: Path, search: Search, text: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    identity = f"- **Identifiant de recherche :** {search.id}"
    next_number = 1
    for report in sorted(directory.glob("rapport-*.md")):
        match = re.fullmatch(r"rapport-(\d+)\.md", report.name)
        if match is None:
            continue
        next_number = max(next_number, int(match[1]) + 1)
        if identity in report.read_text(encoding="utf-8").splitlines():
            report.write_text(text, encoding="utf-8")
            return report
    while True:
        report = directory / f"rapport-{next_number:03d}.md"
        try:
            with report.open("x", encoding="utf-8") as stream:
                stream.write(text)
            return report
        except FileExistsError:
            next_number += 1


def write_search_report(
    storage: SQLiteStorage,
    search: Search,
    coverage: Coverage,
    output_dir: str | Path = "outputs",
    name: str | None = None,
) -> Path:
    """Export facts collected by this finalized Sirene search, grouped by source/name, with one numbered report per search."""
    if search.completed_at is None:
        raise ValueError("Only finalized searches can be exported")
    if coverage.search_id != search.id or coverage.connector != "sirene":
        raise ValueError("Coverage must belong to this Sirene search")
    rows = []
    for result in storage.get_search_results(search.id):
        if result.connector != "sirene":
            continue
        facts = {
            observation.field: observation.value
            for observation in storage.get_observations(result.entity_id)
            if observation.source == result.connector
            and search.started_at <= observation.observed_at <= search.completed_at
        }
        identifiers = storage.get_identifiers(result.entity_id)
        ids = {
            scheme: ", ".join(
                sorted(
                    {
                        item.value
                        for item in identifiers
                        if item.scheme == scheme and item.source == "sirene"
                    }
                )
            )
            for scheme in ("siret", "siren")
        }
        rows.append(
            (facts.get("name") or ids["siret"] or "Établissement sans nom", ids, facts)
        )
    rows.sort(key=lambda row: (row[0].casefold(), row[1]["siret"]))
    started = search.started_at.astimezone(ZoneInfo("Europe/Paris"))
    coverage_text = {
        CoverageStatus.COMPLETE_FOR_SOURCE: "Recherche terminée pour la source et les filtres choisis.",
        CoverageStatus.TRUNCATED: "Résultats partiels : limite de pages atteinte. Cette liste n'est pas exhaustive.",
        CoverageStatus.PARTIAL: "Résultats partiels : la collecte a été interrompue par une erreur.",
        CoverageStatus.FAILED: "Recherche échouée : aucun résultat exploitable confirmé.",
    }[coverage.status]
    lines = [
        "# Rapport Argos — SIRENE",
        "",
        f"**Recherche :** {_safe(search.scope.activity)} — {_safe(search.scope.location)}",
        "",
        f"- **Date :** {started:%d/%m/%Y à %H:%M:%S} (Europe/Paris)",
        f"- **Établissements enregistrés :** {len(rows)}",
        f"- **Pages consultées :** {coverage.pages_processed}",
        "",
        f"**Couverture :** {coverage_text}",
        "",
        "## Établissements",
        "",
        "Classement alphabétique. Les champs ci-dessous décrivent l'état courant reçu lors de cette recherche.",
        "Une requête portant sur les périodes historiques peut aussi retrouver des établissements fermés ou ayant changé d'activité.",
        "",
    ]
    for number, (establishment_name, identifiers, facts) in enumerate(rows, 1):
        status = facts.get("administrative_status", "")
        status = {"A": "Actif", "F": "Fermé"}.get(status, status or "Non renseigné")
        lines.extend(
            [
                f"### {number}. {_safe(establishment_name)}",
                "",
                f"- **SIRET :** {_safe(identifiers['siret'] or 'Non renseigné')}",
                f"- **SIREN :** {_safe(identifiers['siren'] or 'Non renseigné')}",
                f"- **État administratif :** {_safe(status)}",
                f"- **Activité actuelle (code NAF) :** {_safe(facts.get('activity') or 'Non renseigné')}",
                f"- **Adresse :** {_safe(format_address(facts.get('address', '')) or 'Non renseignée')}",
                "",
            ]
        )
    if not rows:
        lines.extend(["Aucun établissement enregistré pour cette recherche.", ""])
    if coverage.errors:
        lines.extend(["## Erreurs de collecte", ""])
        lines.extend(f"- {_safe(error)}" for error in coverage.errors)
        lines.append("")
    if coverage.exclusions:
        lines.extend(["## Exclusions", ""])
        lines.extend(
            f"- {_safe(reason)} : {count}"
            for reason, count in sorted(coverage.exclusions.items())
        )
        lines.append("")
    lines.extend(
        [
            "## Traçabilité",
            "",
            "- **Source :** [API SIRENE — INSEE](https://portail-api.insee.fr/catalog/api/2ba0e549-5587-3ef1-9082-99cd865de66f)",
            f"- **Identifiant de recherche :** {search.id}",
            f"- **Requête exécutée :** {_safe(search.query)}",
            "",
            "Ce rapport est un export de la recherche sauvegardée. Sa génération ne déclenche aucun appel à l'API.",
            "",
        ]
    )
    directory = _report_directory(output_dir, search, name)
    return _save_numbered_report(directory, search, "\n".join(lines))
