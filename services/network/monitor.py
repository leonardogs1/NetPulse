import time

from services.network.base import BaseMonitoring

from services.network.models import (
        InterfaceStats,
        NetworkInfo,
        NetworkAddress,
        TrafficRates
)


class NetworkMonitor(BaseMonitoring):
    """Per-interface traffic, like the network section of Task Manager."""

    def __init__(self):
        super().__init__()
        self._last_counters = {}
        self._last_time = None

    def collect_all(self) -> list:
        now = time.monotonic()
        counters = self.system.net_io_counters(pernic=True)
        stats = self.system.net_if_stats()
        addrs = self.system.net_if_addrs()
        elapsed = now - self._last_time if self._last_time is not None else 0

        interfaces = []
        for iface, io in counters.items():
            prev = self._last_counters.get(iface)
            nic = stats.get(iface)
            interfaces.append(InterfaceStats(
                name=iface,
                is_up=nic.isup if nic else False,
                network_info=self._get_network_info(addrs.get(iface, [])),
                packets_sent=io.packets_sent,
                packets_recv=io.packets_recv,
                bytes_sent=io.bytes_sent,
                bytes_recv=io.bytes_recv,
                errin=io.errin,
                errout=io.errout,
                dropin=io.dropin,
                dropout=io.dropout,
                duplex=nic.duplex.name if nic else "NIC_DUPLEX_UNKNOWN",
                speed=nic.speed if nic else 0,
                mtu=nic.mtu if nic else 0,
                flags=nic.flags if nic else "",
                traffic_rates=self._rate(io, prev, elapsed)
            ))

        self._last_counters = counters
        self._last_time = now
        return interfaces

    def collect_by_id(self, item_id):
        return next((i for i in self.collect_all() if i.name == item_id), None)

    @staticmethod
    def _get_network_info(addrs: list[tuple]) -> NetworkInfo:
        info = NetworkInfo()
        for addr in addrs:
            info.addresses.append(
                NetworkAddress(
                    family=addr.family,
                    address=addr.address,
                    netmask=addr.netmask,
                    broadcast=addr.broadcast,
                    ptp=addr.ptp
                )
            )
        # info.gateway =  get_gateway()
        return info

    @staticmethod
    def _rate(curr, prev, elapsed: float) -> TrafficRates:
        if prev is None or elapsed <= 0:
            return TrafficRates()

        # Clamp at 0: counters reset when an interface restarts.
        return TrafficRates(
            tx_packet_rate=max(curr.packets_sent - prev.packets_sent, 0) / elapsed,
            rx_packet_rate=max(curr.packets_recv - prev.packets_recv, 0) / elapsed,
            tx_byte_rate=max(curr.bytes_sent - prev.bytes_sent, 0) / elapsed,
            rx_byte_rate=max(curr.bytes_recv - prev.bytes_recv, 0) / elapsed
        )
