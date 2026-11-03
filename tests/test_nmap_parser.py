import pytest
from argos.backend.attack.pentest.nmap_parser import NmapParseError, parse_nmap_xml


def scan(target: str = "127.0.0.1") -> bytes:
    return (
        f'<nmaprun><host><address addr="{target}" addrtype="ipv4"/>'
        '<ports><port protocol="tcp" portid="22"><state state="open"/>'
        '<service name="ssh" version="9.2"/></port>'
        '<port protocol="tcp" portid="80"><state state="closed"/></port>'
        '</ports></host></nmaprun>'
    ).encode()


def test_parse_open_port_and_service() -> None:
    result = parse_nmap_xml(scan(), "127.0.0.1")
    assert result.open_tcp_ports == frozenset({22})
    assert result.ports[0].service == "ssh"
    assert result.ports[0].version == "9.2"


def test_reject_unexpected_target() -> None:
    with pytest.raises(NmapParseError, match="outside"):
        parse_nmap_xml(scan("127.0.0.2"), "127.0.0.1")


def test_reject_doctype_and_large_xml() -> None:
    with pytest.raises(NmapParseError):
        parse_nmap_xml(
            b'<!DOCTYPE x [<!ENTITY e SYSTEM "file:///etc/passwd">]>'
            b"<nmaprun/>",
            "127.0.0.1",
        )
    with pytest.raises(NmapParseError):
        parse_nmap_xml(b"x" * 2_000_001, "127.0.0.1")


def test_reject_malformed_xml() -> None:
    with pytest.raises(NmapParseError):
        parse_nmap_xml(b"<nmaprun>", "127.0.0.1")
