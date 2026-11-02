from dataclasses import replace
from datetime import UTC, datetime, timedelta
from subprocess import CompletedProcess
from unittest.mock import patch

import pytest
from argos.backend.attack.pentest.nmap_runner import NmapRunner, ScanExecutionError
from argos.backend.attack.pentest.planner import ScanPlanner
from argos.backend.core.missions import Mission, MissionState
from argos.backend.core.scope import TargetScope


def active_lab() -> Mission:
    return replace(
        Mission.draft("Local lab", "lab-mandate", datetime.now(UTC) + timedelta(hours=1)),
        state=MissionState.ACTIVE,
    )


def test_default_denies_without_external_mandate_check() -> None:
    with pytest.raises(ScanExecutionError, match="verified"):
        NmapRunner(executable="/usr/bin/nmap").execute(
            active_lab(), TargetScope(("127.0.0.1/32",)),
            "127.0.0.1", ScanPlanner().initial(),
        )


def test_non_loopback_refused_before_subprocess() -> None:
    with patch("argos.backend.attack.pentest.nmap_runner.subprocess.run") as run:
        with pytest.raises(ScanExecutionError, match="loopback"):
            NmapRunner("/usr/bin/nmap").execute(
                active_lab(), TargetScope(("192.168.1.1/32",)),
                "192.168.1.1", ScanPlanner().initial(), mandate_verified=True,
            )
        run.assert_not_called()


def test_local_scan_uses_fixed_non_shell_args_and_parses_xml() -> None:
    xml = b'<nmaprun><host><address addr="127.0.0.1" addrtype="ipv4"/><ports><port protocol="tcp" portid="22"><state state="open"/></port></ports></host></nmaprun>'
    with patch("argos.backend.attack.pentest.nmap_runner.subprocess.run") as run:
        run.return_value = CompletedProcess(args=[], returncode=0, stdout=xml, stderr=b"")
        executed = NmapRunner("/usr/bin/nmap").execute(
            active_lab(), TargetScope(("127.0.0.1/32",)),
            "127.0.0.1", ScanPlanner().initial(), mandate_verified=True,
        )
    assert executed.observation.open_tcp_ports == frozenset({22})
    arguments = run.call_args.args[0]
    assert arguments[-1] == "127.0.0.1"
    assert "-sT" in arguments and "-oX" in arguments
    assert run.call_args.kwargs["shell"] is False
    assert run.call_args.kwargs["timeout"] == 75
    assert "-sV" not in arguments


def test_fail_closed_when_mandate_scope_does_not_match() -> None:
    with pytest.raises(ScanExecutionError, match="scope"):
        NmapRunner("/usr/bin/nmap").execute(
            active_lab(), TargetScope(("127.0.0.2/32",)),
            "127.0.0.1", ScanPlanner().initial(), mandate_verified=True,
        )
