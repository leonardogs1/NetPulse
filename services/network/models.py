import socket
from dataclasses import dataclass, field


def format_bytes(size: int | float | None, decimals: int = 2) -> str:
    if size is None:
    	return "N/A"
    units = ("B", "KiB", "MiB", "GiB", "TiB", "PiB")
    size = float(size)
    for unit in units[:-1]:
        if abs(size) < 1024:
            return f"{size:.{decimals}f} {unit}"
        size /= 1024
    return f"{size:.{decimals}f} {units[-1]}"


@dataclass
class NetworkAddress:
    family: socket.AddressFamily | int
    address: str
    netmask: str | None = None
    broadcast: str | None = None
    ptp: str | None = None


@dataclass(frozen=True, slots=True)
class NetworkInfo:
    """Network configuration associated with an interface"""
    addresses: list[NetworkAddress] = field(default_factory=list)
    gateway: str | None = None
 
    @property
    def ipv4(self) -> list[NetworkAddress]:
        return [
                addr for addr in self.addresses
                if addr.family == socket.AF_INET
        ]
    
    @property
    def ipv6(self) -> list[NetworkAddress]:
        return [
                addr for addr in self.addresses
                if addr.family == socket.AF_INET6
        ]


@dataclass(frozen=True, slots=True)
class InterfaceStats:
    """Network interface state and traffic measurements.

    Traffic counters are cumulative.
    Rates are measured in bytes per second (B/s).
    A rate of None indicates insufficient measurement data.
    """

    name: str
    is_up: bool
    network_info: NetworkInfo

    # Cumulative traffic counters
    packets_sent: int
    packets_recv: int
    bytes_sent: int
    bytes_recv: int

    # Cumulative errors and drops
    errin: int
    errout: int
    dropin: int
    dropout: int

    # Average transfer rates (B/s)
    send_rate: float | None = None
    recv_rate: float | None = None
 
    def __str__(self) -> str:
        status = "UP" if self.is_up else "DOWN"
        
        ipv4 = ", ".join(
                addr.address for addr in self.network_info.ipv4
                ) or "-"
        
        send = (
                f"{format_bytes(self.send_rate)}/s"
                if self.send_rate is not None else "N/A"
        )

        recv = (
                f"{format_bytes(self.recv_rate)}/s"
                if self.recv_rate is not None else "N/A"
	    )
 
        return (
                f"{self.name:<16} "
                f"{status:<6} "
                f"{ipv4:<20} "
                f"bytes sent: {self.bytes_sent} "
                f"bytes recv: {self.bytes_recv} "
                f"TX: {send:>14}  "
                f"RX: {recv:>14}"
        )
