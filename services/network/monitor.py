import socket
import time

from services.network.base import BaseMonitoring

from services.network.models import InterfaceStats, NetworkInfo, NetworkAddress


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
        for iface, io in counters.items():
            prev = self._last_counters.get(iface)
            interfaces.append(InterfaceStats(
                name=iface,
                is_up=stats[iface].isup if iface in stats else False,
                network_info=self._get_network_info(addrs.get(iface, [])),
                packets_sent=io.packets_sent,
                packets_recv=io.packets_recv,
                bytes_sent=io.bytes_sent,
                bytes_recv=io.bytes_recv,
                send_rate=self._rate(io.bytes_sent, prev.bytes_sent if prev else None, elapsed),
                recv_rate=self._rate(io.bytes_recv, prev.bytes_recv if prev else None, elapsed),
                errin=io.errin,
                errout=io.errout,
                dropin=io.dropin,
                dropout=io.dropout
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
        #info.gateway =  get_gateway()
        return info 
 
    @staticmethod
    def _rate(current, previous, elapsed):
        if previous is None or elapsed <= 0:
            return None
        # Clamp at 0: counters reset when an interface restarts.
        return max(current - previous, 0) / elapsed
    
