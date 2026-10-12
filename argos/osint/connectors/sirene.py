"""Minimal client for the official INSEE Sirene API v3.11."""

import os
from typing import Any

import httpx


class SireneConnector:
    """Fetch raw Sirene JSON; an injected HTTP client remains caller-owned."""

    def __init__(self, *, client: httpx.Client | None = None) -> None:
        self._client = client

    def search_establishments(
        self,
        query: str,
        *,
        page_size: int = 20,
        cursor: str = "*",
    ) -> dict[str, Any]:
        """Return one page, preserving etablissements and all header metadata.

        Pass header['curseurSuivant'] as cursor for the next page. Pagination
        ends when header['curseurSuivant'] equals header['curseur'].
        HTTP failures, including 404 (no match), raise httpx.HTTPStatusError.
        """
        if not query.strip():
            raise ValueError("query must not be blank")
        if not 0 <= page_size <= 1000:
            raise ValueError("page_size must be between 0 and 1000 for JSON responses")
        if not cursor.strip():
            raise ValueError("cursor must not be blank")
        api_key = os.environ.get("INSEE_API_KEY", "").strip()
        if not api_key:
            raise ValueError("INSEE_API_KEY is required to call the INSEE Sirene API")

        get = httpx.get if self._client is None else self._client.get
        response = get(
            "https://api.insee.fr/api-sirene/3.11/siret",
            params={"q": query, "nombre": page_size, "curseur": cursor},
            headers={
                "Accept": "application/json",
                "X-INSEE-Api-Key-Integration": api_key,
            },
            timeout=10.0,
            follow_redirects=False,
        )
        response.raise_for_status()
        try:
            data = response.json()
        except ValueError as error:
            raise ValueError("Invalid JSON response from the INSEE Sirene API") from error
        if (
            not isinstance(data, dict)
            or not isinstance(data.get("header"), dict)
            or not isinstance(data.get("etablissements"), list)
            or any(not isinstance(item, dict) for item in data["etablissements"])
        ):
            raise ValueError("Invalid Sirene response: expected header and etablissements")
        return data
