import ipaddress
import sys
from time import sleep

from services.network.models import format_bytes
from services.network.monitor import NetworkMonitor

WIDTH = 78
LABEL_W = 14
COL_W = 18
USE_COLOR = sys.stdout.isatty()

FAMILY_NAMES = {
    "AF_INET": "IPv4",
    "AF_INET6": "IPv6",
    "AF_PACKET": "MAC",
    "AF_LINK": "MAC",
}


def style(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text


def fmt(value) -> str:
    return "-" if value is None else str(value)


def family_name(family) -> str:
    name = getattr(family, "name", str(family))
    return FAMILY_NAMES.get(name, name)


def with_prefix(address: str, netmask: str | None) -> str:
    """Render an address in CIDR form, e.g. 192.168.1.10/24."""
    if netmask is None:
        return address
    try:
        bits = bin(int(ipaddress.ip_address(netmask))).count("1")
    except ValueError:
        return address
    return f"{address}/{bits}"


def per_second(value: float | None, as_bytes: bool = False) -> str:
    if value is None:
        return "N/A"
    return f"{format_bytes(value)}/s" if as_bytes else f"{value:,.1f}/s"


def print_header(iface) -> None:
    status = "UP" if iface.is_up else "DOWN"
    gap = max(WIDTH - len(iface.name) - len(status) - 4, 1)
    rule = style("═" * WIDTH, "2")

    print(rule)
    print(
        f" {style(iface.name, '1')}{' ' * gap}"
        f"{style('● ' + status, '32' if iface.is_up else '31')} "
    )
    print(rule)


def print_addresses(network_info) -> None:
    print(style(" Addresses", "1;36"))

    headers = ("Family", "Address", "Broadcast", "P2P")
    rows = [
        (
            family_name(addr.family),
            with_prefix(addr.address, addr.netmask),
            fmt(addr.broadcast),
            fmt(addr.ptp),
        )
        for addr in network_info.addresses
    ]

    if rows:
        widths = [
            max(len(cell) for cell in (header, *(row[i] for row in rows)))
            for i, header in enumerate(headers)
        ]
        line = "  ".join(h.ljust(w) for h, w in zip(headers, widths))
        print("   " + style(line.rstrip(), "2"))
        for row in rows:
            line = "  ".join(c.ljust(w) for c, w in zip(row, widths))
            print("   " + line.rstrip())
    else:
        print("   none")

    print(f"   {'Gateway':<{LABEL_W}}{fmt(network_info.gateway)}")


def print_table(title: str, columns: tuple[str, ...], rows: list[tuple]) -> None:
    header = f" {title:<{LABEL_W + 2}}" + "".join(f"{c:>{COL_W}}" for c in columns)
    print(style(header, "1;36"))
    for label, *values in rows:
        print(f"   {label:<{LABEL_W}}" + "".join(f"{v:>{COL_W}}" for v in values))


def print_interface(iface) -> None:
    rates = iface.traffic_rates

    print_header(iface)
    print_addresses(iface.network_info)
    print()
    print_table("Traffic", ("Sent", "Received"), [
        ("Packets", f"{iface.packets_sent:,}", f"{iface.packets_recv:,}"),
        ("Bytes", format_bytes(iface.bytes_sent), format_bytes(iface.bytes_recv)),
        ("Errors", f"{iface.errout:,}", f"{iface.errin:,}"),
        ("Drops", f"{iface.dropout:,}", f"{iface.dropin:,}"),
    ])
    print()
    print_table("Rates", ("TX", "RX"), [
        ("Packets", per_second(rates.tx_packet_rate), per_second(rates.rx_packet_rate)),
        ("Bytes", per_second(rates.tx_byte_rate, as_bytes=True),
                  per_second(rates.rx_byte_rate, as_bytes=True)),
    ])
    print()


if __name__ == '__main__':
    network_monitor = NetworkMonitor()
    network_monitor.collect_all()  # seed counters so the next call can compute rates

    sleep(1)

    interfaces = network_monitor.collect_all()

    print(style(f" Interfaces ({len(interfaces)})", "1"))
    for iface in interfaces:
        print(f"   {iface}")
    print()

    for iface in interfaces:
        print(f"{type(iface)}")
        print_interface(iface)

    # For Evaluating ipv6 addresses compared to `ip addr`
    print("=================")
    print(f"{interfaces[1].network_info}")
