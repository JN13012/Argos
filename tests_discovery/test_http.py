import socket
import ssl

import httpx
import pytest

from argos.discovery.http import FetchError, RequestBudget, resolve_public, validated_url
from conftest import response


@pytest.mark.parametrize("url", ["file:///etc/passwd", "ftp://external.example/", "http://localhost/",
                               "http://internal.local/", "http://user:pass@external.example/",
                               "https://external.example:444/", "http://external.example/\nfoo",
                               "http://external.example\\@127.0.0.1/"])
def test_invalid_urls_rejected(url):
    with pytest.raises(FetchError):
        validated_url(url)


@pytest.mark.parametrize("ip", ["127.0.0.1", "10.0.0.1", "169.254.169.254", "192.168.1.1",
                               "::1", "fc00::1", "::ffff:127.0.0.1", "224.0.0.1"])
def test_nonpublic_literals_never_contacted(ip, http_factory):
    calls = []
    client = http_factory(lambda request: calls.append(request), resolver=lambda _h, _p: ip)
    with pytest.raises(FetchError, match="non_public_address"):
        client.get("https://external.example/")
    assert calls == []


def test_mixed_public_private_dns_fails_closed(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *_a, **_k: [
        (2, 1, 6, "", ("93.184.216.34", 443)), (2, 1, 6, "", ("10.0.0.1", 443))])
    with pytest.raises(FetchError, match="non_public_address"):
        resolve_public("external.example", 443)


def test_dns_pinning_preserves_host_and_tls_hostname(http_factory):
    calls, resolutions = [], []
    def resolver(host, port):
        resolutions.append((host, port))
        return "93.184.216.34"
    def handler(request):
        calls.append(request)
        return response("OK")
    result = http_factory(handler, resolver=resolver).get("https://external.example/")
    assert result.url == "https://external.example/"
    assert resolutions == [("external.example", 443)]
    assert calls[0].url.host == "93.184.216.34"
    assert calls[0].headers["host"] == "external.example"
    assert calls[0].extensions["sni_hostname"] == "external.example"
    assert calls[0].headers["accept-encoding"] == "identity"


def test_redirect_outside_domain_is_not_requested(http_factory):
    calls = []
    def handler(request):
        calls.append(request)
        return response(status=302, headers={"location": "https://other.example/"})
    with pytest.raises(FetchError, match="redirect_outside_domain"):
        http_factory(handler).get("https://external.example/", allowed_hosts={"external.example"})
    assert len(calls) == 1


def test_private_redirect_blocked_with_unrestricted_hosts(http_factory):
    calls = []
    def handler(request):
        calls.append(request)
        return response(status=302, headers={"location": "http://127.0.0.1/"})
    def resolver(host, port):
        return host if host == "127.0.0.1" else "93.184.216.34"
    with pytest.raises(FetchError, match="non_public_address"):
        http_factory(handler, resolver=resolver).get("http://external.example/")
    assert len(calls) == 1


@pytest.mark.parametrize("target,code", [("http://external.example/", "https_downgrade"),
                                       ("https://external.example/", "redirect_limit")])
def test_downgrade_and_redirect_limits(target, code, http_factory):
    client = http_factory(lambda _r: response(status=302, headers={"location": target}), max_redirects=1)
    with pytest.raises(FetchError, match=code):
        client.get("https://external.example/")


@pytest.mark.parametrize("headers,body,code", [({"content-length": "200"}, "tiny", "response_too_large"),
                                              ({}, "x" * 101, "response_too_large"),
                                              ({"content-encoding": "gzip"}, "tiny", "compressed_response_refused")])
def test_response_limits(headers, body, code, http_factory):
    with pytest.raises(FetchError, match=code):
        http_factory(lambda _r: response(body, headers=headers), max_bytes=100).get("https://external.example/")


def test_timeout_is_distinct_from_invalid_certificate(http_factory):
    def timeout(request):
        raise httpx.ReadTimeout("Timeout", request=request)
    with pytest.raises(FetchError, match="timeout"):
        http_factory(timeout).get("https://external.example/")
    def invalid_certificate(request):
        raise httpx.ConnectError("TLS", request=request) from ssl.SSLCertVerificationError("Invalid certificate")
    with pytest.raises(FetchError, match="tls_certificate_invalid"):
        http_factory(invalid_certificate).get("https://external.example/")


def test_request_budget_includes_redirects(http_factory):
    calls = []
    def handler(request):
        calls.append(request)
        return response(status=302, headers={"location": "/other"})
    with pytest.raises(FetchError, match="request_budget_exhausted"):
        http_factory(handler).get("https://external.example/", budget=RequestBudget(1))
    assert len(calls) == 1
