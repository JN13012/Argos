"""Deterministic single-target IP scope checks, independent of scan tooling."""

from dataclasses import dataclass
from ipaddress import ip_address, ip_network


@dataclass(frozen=True)
class TargetScope:
    networks: tuple[str, ...]
    excluded: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.networks:
            raise ValueError("At least one explicitly authorized network is required")
        for value in (*self.networks, *self.excluded):
            network = ip_network(value, strict=True)
            if network.prefixlen == 0:
                raise ValueError("Unbounded target networks are not accepted")

    def permits(self, address: str) -> bool:
        """Only numeric addresses are accepted; DNS requires separate controls."""
        try:
            target = ip_address(address)
        except ValueError:
            return False
        return (
            any(target in ip_network(net) for net in self.networks)
            and not any(target in ip_network(net) for net in self.excluded)
        )
