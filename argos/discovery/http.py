"""Bounded public HTTP GETs; pin checked DNS addresses through HTTPX's SNI extension."""

from dataclasses import dataclass
import ipaddress
import socket
import ssl
import time
from typing import Callable
from urllib.parse import urljoin

import httpx


USER_AGENT = "ArgosDiscovery/0.1 (+https://github.com/JN13012/Argos; public-business-qualification)"


class FetchError(ValueError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def validated_url(raw: str) -> httpx.URL:
    if len(raw) > 2000 or any(ord(c) <= 32 or ord(c) == 127 for c in raw) or "\\" in raw:
        raise FetchError("invalid_url")
    try:
        url = httpx.URL(raw)
        if (url.scheme not in {"http", "https"} or not url.host or url.userinfo
                or url.port not in {None, 80 if url.scheme == "http" else 443}):
            raise FetchError("invalid_url")
        host = url.host.lower().rstrip(".")
        if host == "localhost" or host.endswith((".localhost", ".local", ".internal")) or "." not in host and ":" not in host:
            raise FetchError("non_public_host")
        return url.copy_with(host=host, fragment=None)
    except (httpx.InvalidURL, ValueError) as exc:
        if isinstance(exc, FetchError):
            raise
        raise FetchError("invalid_url") from exc


def public_ip(value: str) -> bool:
    ip = ipaddress.ip_address(value)
    if not ip.is_global or ip.is_multicast:
        return False
    if isinstance(ip, ipaddress.IPv6Address) and (ip.ipv4_mapped or ip.sixtofour or ip.teredo):
        return False
    return True


def resolve_public(host: str, port: int) -> str:
    try:
        try:
            addresses = [str(ipaddress.ip_address(host))]
        except ValueError:
            addresses = sorted({entry[4][0] for entry in
                                socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)})
        if not addresses or not all(public_ip(address) for address in addresses):
            raise FetchError("non_public_address")
        return addresses[0]
    except socket.gaierror as exc:
        raise FetchError("dns_error") from exc


def certificate_error(exc: BaseException) -> bool:
    while exc is not None:
        if isinstance(exc, ssl.SSLCertVerificationError):
            return True
        exc = exc.__cause__ or exc.__context__
    return False


@dataclass
class FetchedPage:
    url: str
    status_code: int
    headers: dict[str, str]
    body: bytes
    response_ms: int
    redirects: list[str]


@dataclass
class RequestBudget:
    remaining: int = 16

    def consume(self):
        if self.remaining <= 0:
            raise FetchError("request_budget_exhausted")
        self.remaining -= 1


class PublicHttpClient:
    def __init__(self, *, transport: httpx.BaseTransport | None = None,
                 resolver: Callable[[str, int], str] = resolve_public,
                 max_bytes: int = 1024 * 1024, max_redirects: int = 3,
                 timeout: float = 5.0):
        self.resolver = resolver
        self.max_bytes = max_bytes
        self.max_redirects = max_redirects
        self.timeout = timeout
        self.client = httpx.Client(transport=transport, timeout=timeout, trust_env=False,
                                   follow_redirects=False,
                                   limits=httpx.Limits(max_connections=1, max_keepalive_connections=0))

    def close(self):
        self.client.close()

    def get(self, raw_url: str, *, allowed_hosts: set[str] | None = None,
            permit: Callable[[str], bool] | None = None,
            budget: RequestBudget | None = None) -> FetchedPage:
        url = validated_url(raw_url)
        started, redirects = time.monotonic(), []
        for hop in range(self.max_redirects + 1):
            if allowed_hosts is not None and url.host not in allowed_hosts:
                raise FetchError("redirect_outside_domain")
            if permit is not None and not permit(str(url)):
                raise FetchError("robots_disallowed")
            if budget:
                budget.consume()
            address = self.resolver(url.host, url.port or (443 if url.scheme == "https" else 80))
            if not public_ip(address):
                raise FetchError("non_public_address")
            # No second DNS lookup: connect to the checked literal address, preserving
            # the original HTTP Host and TLS certificate hostname. Never disable TLS.
            pinned = url.copy_with(host=address)
            self.client.cookies.clear()
            try:
                with self.client.stream("GET", pinned,
                                        headers={"Host": url.netloc.decode("ascii"),
                                                 "User-Agent": USER_AGENT, "Accept-Encoding": "identity"},
                                        extensions={"sni_hostname": url.host}) as response:
                    if response.status_code in {301, 302, 303, 307, 308}:
                        location = response.headers.get("location")
                        if not location or hop == self.max_redirects:
                            raise FetchError("redirect_limit_or_missing_location")
                        target = validated_url(urljoin(str(url), location))
                        if url.scheme == "https" and target.scheme == "http":
                            raise FetchError("https_downgrade")
                        redirects.append(str(url))
                        url = target
                        continue
                    if response.headers.get("content-encoding", "identity").lower() not in {"", "identity"}:
                        raise FetchError("compressed_response_refused")
                    size = response.headers.get("content-length")
                    if size and (not size.isdigit() or int(size) > self.max_bytes):
                        raise FetchError("response_too_large")
                    chunks, total = [], 0
                    for chunk in response.iter_raw(chunk_size=65536):
                        total += len(chunk)
                        if total > self.max_bytes:
                            raise FetchError("response_too_large")
                        if time.monotonic() - started > self.timeout * 3:
                            raise FetchError("response_deadline")
                        chunks.append(chunk)
                    return FetchedPage(str(url), response.status_code, dict(response.headers),
                                       b"".join(chunks), round((time.monotonic() - started) * 1000), redirects)
            except httpx.HTTPError as exc:
                raise FetchError("tls_certificate_invalid" if certificate_error(exc) else
                                 "timeout" if isinstance(exc, httpx.TimeoutException) else "http_error") from exc
        raise FetchError("redirect_limit_or_missing_location")

    def get_json(self, url: str):
        import json

        page = self.get(url, allowed_hosts={validated_url(url).host})
        if page.status_code != 200:
            raise FetchError(f"http_status_{page.status_code}")
        try:
            return json.loads(page.body)
        except (ValueError, UnicodeError, RecursionError) as exc:
            raise FetchError("invalid_json") from exc
