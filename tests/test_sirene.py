import httpx
import pytest

from argos.osint.connectors import SireneConnector

QUERY = "periode(etatAdministratifEtablissement:A) AND codeCommuneEtablissement:13055"


@pytest.fixture(autouse=True)
def api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INSEE_API_KEY", "test-api-key")


def test_search_sends_official_request_and_preserves_json() -> None:
    payload = {
        "header": {"statut": 200, "message": "OK", "total": 1, "nombre": 1},
        "etablissements": [{
            "siret": "12345678900012",
            "siren": "123456789",
            "adresseEtablissement": {"codeCommuneEtablissement": "13055"},
            "periodesEtablissement": [{"etatAdministratifEtablissement": "A"}],
        }],
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert str(request.url.copy_with(query=None)) == (
            "https://api.insee.fr/api-sirene/3.11/siret"
        )
        assert dict(request.url.params) == {"q": QUERY, "nombre": "20", "curseur": "*"}
        assert request.headers["X-INSEE-Api-Key-Integration"] == "test-api-key"
        assert request.headers["Accept"] == "application/json"
        assert "Authorization" not in request.headers
        return httpx.Response(200, json=payload)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        result = SireneConnector(client=client).search_establishments(query=QUERY)
        assert result == payload
        assert not client.is_closed


def test_valid_empty_page_without_optional_metadata() -> None:
    payload = {"header": {"statut": 200, "message": "OK"}, "etablissements": []}
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json=payload))

    with httpx.Client(transport=transport) as client:
        assert SireneConnector(client=client).search_establishments(QUERY) == payload


@pytest.mark.parametrize("status", [400, 401, 403, 404, 406, 414, 429, 500, 503])
def test_http_errors_are_reported(status: int) -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(status, text="API error"))

    with httpx.Client(transport=transport) as client:
        with pytest.raises(httpx.HTTPStatusError) as raised:
            SireneConnector(client=client).search_establishments(QUERY)

    assert raised.value.response.status_code == status
    assert str(status) in str(raised.value)


@pytest.mark.parametrize("key", [None, "", "   "])
def test_missing_api_key_prevents_network_call(
    monkeypatch: pytest.MonkeyPatch, key: str | None,
) -> None:
    if key is None:
        monkeypatch.delenv("INSEE_API_KEY")
    else:
        monkeypatch.setenv("INSEE_API_KEY", key)

    def unexpected_request(*args: object, **kwargs: object) -> None:
        pytest.fail("A missing API key must fail before any network call")

    monkeypatch.setattr(httpx, "get", unexpected_request)
    with pytest.raises(ValueError, match="INSEE_API_KEY is required"):
        SireneConnector().search_establishments(QUERY)


def test_cursor_can_be_used_for_next_page_and_signals_completion() -> None:
    cursors = []

    def handler(request: httpx.Request) -> httpx.Response:
        cursor = request.url.params["curseur"]
        cursors.append(cursor)
        assert request.url.params["q"] == QUERY
        assert request.url.params["nombre"] == "1"
        assert request.headers["X-INSEE-Api-Key-Integration"] == "test-api-key"
        return httpx.Response(200, json={
            "header": {
                "statut": 200, "total": 1, "nombre": 1 if cursor == "*" else 0,
                "curseur": cursor, "curseurSuivant": "next+/=",
            },
            "etablissements": [{"siret": "12345678900012"}] if cursor == "*" else [],
        })

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        connector = SireneConnector(client=client)
        first = connector.search_establishments(QUERY, page_size=1)
        assert first["header"]["total"] == 1
        assert first["header"]["curseur"] != first["header"]["curseurSuivant"]
        last = connector.search_establishments(
            QUERY, page_size=1, cursor=first["header"]["curseurSuivant"],
        )

    assert cursors == ["*", "next+/="]
    assert last["etablissements"] == []
    assert last["header"]["curseur"] == last["header"]["curseurSuivant"]


@pytest.mark.parametrize("body", ["not JSON", "[]", '{"header": {}}'])
def test_malformed_responses_fail_clearly(body: str) -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(200, text=body))

    with httpx.Client(transport=transport) as client:
        with pytest.raises(ValueError, match="Invalid"):
            SireneConnector(client=client).search_establishments(QUERY)
