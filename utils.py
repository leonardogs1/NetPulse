UNITS = ("B", "KB", "MB", "GB", "TB")


def format_bytes(num):
    """Turn a byte count into a short human-readable string, e.g. 1536 -> '1.5 KB'."""
    for unit in UNITS[:-1]:
        if abs(num) < 1024:
            return f"{num:.1f} {unit}"
        num /= 1024
    return f"{num:.1f} {UNITS[-1]}"
