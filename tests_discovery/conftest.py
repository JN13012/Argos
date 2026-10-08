"""Discovery tests must never open a real socket or resolve DNS."""

from datetime import datetime
import json
from pathlib import Path
import socket

import httpx
import pytest

from argos.discovery.http import PublicHttpClient
from argos.discovery.models import SourceReference
from argos.discovery.normalize import normalize_establishment


ROOT = Path(__file__).resolve().parents[1]
COLLECTED = datetime.fromisoformat("2026-10-08T00:00:00+00:00")


@pytest.fixture(autouse=True)
def forbid_network(monkeypatch):
    def forbidden(*_args, **_kwargs):
        raise AssertionError("Tests must not use the network")
    for name in ("socket", "create_connection", "getaddrinfo"):
        monkeypatch.setattr(socket, name, forbidden)


@pytest.fixture
def business():
    company = json.loads((ROOT / "examples/discovery/companies.json").read_text())["results"][1]
    return normalize_establishment(company, company["matching_etablissements"][0],
                                   SourceReference(source_name="Synthetic test", source_url="fixture:test", collected_at=COLLECTED))


@pytest.fixture
def http_factory():
    clients = []

    def factory(handler, **kwargs):
        client = PublicHttpClient(transport=httpx.MockTransport(handler),
                                  resolver=kwargs.pop("resolver", lambda _host, _port: "93.184.216.34"), **kwargs)
        clients.append(client)
        return client
    yield factory
    for client in clients:
        client.close()


def response(body="", status=200, headers=None):
    return httpx.Response(status, headers=headers or {"content-type": "text/html"},
                          stream=httpx.ByteStream(body.encode() if isinstance(body, str) else body))
