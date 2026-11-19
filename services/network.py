import socket
import time
from dataclasses import dataclass

from services.base import BaseMonitoring
from utils import format_bytes


@dataclass
class InterfaceStats:
    name: str
    is_up: bool
    ipv4: str
    bytes_sent: int
    bytes_recv: int
    send_rate: float  # bytes per second since the previous collect
    recv_rate: float

    def __str__(self):
        status = "up" if self.is_up else "down"
        return (
            f"{self.name:<16} {status:<5} {self.ipv4 or '-':<15} "
            f"send {format_bytes(self.send_rate)}/s  "
            f"recv {format_bytes(self.recv_rate)}/s"
        )


class NetworkMonitor(BaseMonitoring):
    """Per-interface traffic, like the network section of Task Manager."""

    def __init__(self):
        super().__init__()
        self._last_counters = {}
        self._last_time = None

    def collect_all(self):
        now = time.monotonic()
        counters = self.system.net_io_counters(pernic=True)
        stats = self.system.net_if_stats()
        addrs = self.system.net_if_addrs()
        elapsed = now - self._last_time if self._last_time is not None else 0

        interfaces = []
        for name, io in counters.items():
            prev = self._last_counters.get(name)
            interfaces.append(InterfaceStats(
                name=name,
                is_up=stats[name].isup if name in stats else False,
                ipv4=self._ipv4(addrs.get(name, [])),
                bytes_sent=io.bytes_sent,
                bytes_recv=io.bytes_recv,
                send_rate=self._rate(io.bytes_sent, prev.bytes_sent if prev else None, elapsed),
                recv_rate=self._rate(io.bytes_recv, prev.bytes_recv if prev else None, elapsed),
            ))

        self._last_counters = counters
        self._last_time = now
        return interfaces

    def collect_by_id(self, item_id):
        return next((i for i in self.collect_all() if i.name == item_id), None)

    @staticmethod
    def _rate(current, previous, elapsed):
        if previous is None or elapsed <= 0:
            return 0.0
        # Clamp at 0: counters reset when an interface restarts.
        return max(current - previous, 0) / elapsed

    @staticmethod
    def _ipv4(addrs):
        for addr in addrs:
            if addr.family == socket.AF_INET:
                return addr.address
        return ""
