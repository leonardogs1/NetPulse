# NetPulse

NetPulse is a desktop network monitor, similar to the network view in Windows Task Manager. It shows every network interface on your computer and how much data each one is sending and receiving, updated every second.

---

## Contents

1. [What's included](#whats-included)
2. [Requirements](#requirements)
3. [Quick start](#quick-start)
4. [Step-by-step setup](#step-by-step-setup)
5. [Using NetPulse](#using-netpulse)
6. [Options](#options)
7. [Troubleshooting](#troubleshooting)
8. [Limitations](#limitations)
9. [Project layout](#project-layout)

---

## What's included

The current version (1.0.0) has a single **Network** tab with a live table of your network interfaces. For each interface it shows:

- Whether it's up or down
- Its IPv4 address
- Current send and receive speed
- Total data sent and received since the interface came up

The table refreshes every second. Everything runs locally: NetPulse only reads statistics from your operating system and never sends data anywhere.

---

## Requirements

| Requirement      | Details                                                          |
|------------------|------------------------------------------------------------------|
| Operating system | Linux. Tested on Ubuntu 22.04 (Wayland session).                  |
| Python           | 3.10 or newer                                                    |
| Python packages  | `psutil`, `PyQt6`, `pyqt6_sip` (installed in step 3 below)        |

Check your Python version with:

```bash
python3 --version
```

---

## Quick start

If you've set up Python projects before, these commands take you from a fresh folder to a running app:

```bash
cd NetPulse
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

If any step fails, follow the detailed steps below or see [Troubleshooting](#troubleshooting).

---

## Step-by-step setup

### 1. Open a terminal in the project folder

```bash
cd path/to/NetPulse
```

### 2. Create and activate a virtual environment

A virtual environment keeps NetPulse's packages separate from the rest of your system.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Your prompt now starts with `(.venv)`. Run the `source` command again each time you open a new terminal to work on NetPulse.

If `python3 -m venv` fails with "ensurepip is not available", install the venv module and try again:

```bash
sudo apt install python3-venv
```

### 3. Install the packages

```bash
pip install -r requirements.txt
```

This installs:

| Package   | Version | Purpose                             |
|-----------|---------|-------------------------------------|
| psutil    | 7.2.2   | Reads network statistics from the OS |
| PyQt6     | 6.12.1  | Draws the window and table          |
| pyqt6_sip | 13.13.1 | Support library required by PyQt6   |

### 4. Run NetPulse

```bash
python app.py
```

A window titled **NetPulse** opens on the **Network** tab. Send and receive speeds read `0.0 B/s` for the first second, then fill in.

### 5. Close NetPulse

Close the window with its **X** button. The app exits and you get your terminal prompt back.

When you're finished, you can leave the virtual environment with:

```bash
deactivate
```

---

## Using NetPulse

### The Network tab

Each row is one network interface. Each column means:

| Column             | Meaning                                                                    |
|--------------------|----------------------------------------------------------------------------|
| **Interface**      | The interface's name as the OS reports it (see the examples below).        |
| **Status**         | `Up` if the interface is enabled, `Down` if it's disabled or unused.       |
| **IPv4**           | The interface's IPv4 address, or `-` if it has none.                       |
| **Send**           | Data sent per second, measured over the last refresh.                      |
| **Receive**        | Data received per second, measured over the last refresh.                  |
| **Total sent**     | All data sent through this interface since it came up (usually since the computer started). |
| **Total received** | All data received through this interface since it came up (usually since the computer started). |

### Common interface names

| Name looks like            | What it is                                                         |
|----------------------------|--------------------------------------------------------------------|
| `lo`                       | Loopback: traffic between programs on your own computer.           |
| `wlp…`, `wlan…`            | Wi-Fi adapter.                                                     |
| `enp…`, `eth…`             | Wired Ethernet adapter.                                            |
| `docker0`, `br-…`          | Virtual bridges created by Docker. Show `Down` with no containers running. |
| `virbr0`                   | Virtual bridge created by virtual-machine software (libvirt/KVM).  |
| `tailscale0`, `tun…`, `wg…` | VPN tunnels.                                                      |

### Units

- Speeds are in **bytes per second** (`KB/s`, `MB/s`). Windows Task Manager shows **bits** per second (`Kbps`, `Mbps`). To compare the two, multiply NetPulse's number by 8.
- Sizes use steps of 1024, so 1 KB = 1024 bytes and 1 MB = 1024 KB.

### Window

- Drag the window's edges to resize it. The columns stretch to fill the width.
- Click a row to highlight it. The highlight stays in place while the numbers update.
- The status bar at the bottom shows the app version.

---

## Options

NetPulse has no command-line flags or settings screen yet. You can change its behaviour in two ways.

### Change the refresh rate or window size

Edit these values and restart the app:

| Setting                  | File                                                 | Default      | Effect                                         |
|--------------------------|------------------------------------------------------|--------------|------------------------------------------------|
| `REFRESH_MS`             | [ui/network_view.py](ui/network_view.py)             | `1000`       | How often the table updates, in milliseconds. `500` means twice a second. |
| `APP_SIZE`               | [app.py](app.py)                                     | `(800, 400)` | Window width and height in pixels when the app opens. |

### Print to the terminal instead of opening a window

Use this to check your network quickly, or over SSH where no window can open. With your virtual environment activated, run this from the project folder:

```bash
python -c "
from services.network.monitor import NetworkMonitor
import time
m = NetworkMonitor()
m.collect_all()   # first reading
time.sleep(1)     # wait so speeds can be measured
m.print_all()
"
```

Example output:

```
lo               UP     127.0.0.1            bytes sent: 4281893 bytes recv: 4281893 TX:       0.00 B/s  RX:       0.00 B/s
wlp0s20f3        UP     10.1.10.204          bytes sent: 320723266 bytes recv: 1399806301 TX:     1.35 KiB/s  RX:     1.99 KiB/s
docker0          DOWN   172.17.0.1           bytes sent: 0 bytes recv: 0 TX:       0.00 B/s  RX:       0.00 B/s
```

To show a single interface, replace `m.print_all()` with `m.print_by_id("wlp0s20f3")`, using an interface name from your own list.

---

## Troubleshooting

### App crashes with `GLib-GIO-ERROR … antialiasing`

```
GLib-GIO-ERROR **: Settings schema 'org.gnome.settings-daemon.plugins.xsettings' does not contain a key named 'antialiasing'
Trace/breakpoint trap (core dumped)
```

**Cause:** you ran the app from the built-in terminal of the Snap version of VS Code. That terminal passes Snap-specific GTK settings to every program it starts, and they clash with your system's GTK. Other GTK and Qt apps started from that terminal crash the same way. It isn't a bug in NetPulse.

**Fix, choose one:**

- **Quickest:** run `python app.py` from Ubuntu's own **Terminal** app.
- **Keep using VS Code's terminal:** add the following to your VS Code user settings (press `Ctrl+Shift+P`, choose **Preferences: Open User Settings (JSON)**). Then close and reopen the terminal.

  ```json
  "terminal.integrated.env.linux": {
      "GSETTINGS_SCHEMA_DIR": null,
      "GTK_PATH": null,
      "GTK_EXE_PREFIX": null,
      "GIO_MODULE_DIR": null,
      "GTK_IM_MODULE_FILE": null,
      "GDK_PIXBUF_MODULE_FILE": null,
      "GDK_PIXBUF_MODULEDIR": null,
      "LOCPATH": null,
      "XDG_DATA_DIRS": "/usr/share/ubuntu:/usr/local/share/:/usr/share/:/var/lib/snapd/desktop"
  }
  ```

- **Permanent:** uninstall the Snap version of VS Code and install the `.deb` package from [code.visualstudio.com](https://code.visualstudio.com/download).

### `ModuleNotFoundError: No module named 'psutil'` (or `'PyQt6'`)

The packages aren't installed in the environment you're running from. Activate the virtual environment and install them:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### `Could not load the Qt platform plugin "xcb"`

This appears on X11 sessions (not Wayland) when a system library that Qt needs is missing. Install it:

```bash
sudo apt install libxcb-cursor0
```

### All speeds show `0.0 B/s`

- **Right after starting:** this is normal. Speeds need two readings, so wait one second.
- **For one interface:** that interface has no traffic. `Down` interfaces and unused virtual bridges always show 0.
- **For every interface, including your Wi-Fi or Ethernet:** check that you're connected to a network.

### An interface I expected isn't listed

NetPulse lists every interface the OS currently reports. An interface that doesn't exist yet, such as a USB adapter that isn't plugged in or a VPN that isn't connected, isn't listed. Once the OS detects it, it appears in the table within a second, with no restart needed.

---

## Limitations

These features aren't in version 1.0.0:

- **No per-application usage.** NetPulse shows traffic per interface, not per program. Measuring bandwidth per program on Linux requires administrator (root) access.
- **No connections list.** It doesn't yet show which programs have open network connections.
- **No graphs.** Speeds are numbers only, with no history chart.
- **No sorting.** The table can't be sorted by clicking a column header.
- **Can't disable interfaces.** NetPulse only reads statistics. It can't turn interfaces on or off.

---

## Project layout

For anyone who wants to read or extend the code:

```
NetPulse/
├── app.py               # Start here: opens the main window and its tabs
├── requirements.txt     # Python packages to install
├── images/              # App icon
├── services/            # Data collection (no GUI code)
│   └── network/
│       ├── base.py      # BaseMonitoring: the rules every monitor follows
│       ├── models.py    # Dataclasses that hold interface data, plus format_bytes()
│       ├── monitor.py   # NetworkMonitor: reads interface statistics
│       └── utils.py     # format_bytes(): turns 1536 into "1.5 KB"
└── ui/                  # Windows and widgets
    └── network_view.py  # The Network tab's table
```

### services/network

Reads interface stats from psutil. No GUI code, so it works from a script too.

- `monitor.py`: `NetworkMonitor`. `collect_all()` returns a list of `InterfaceStats`, `collect_by_id(name)` returns one or `None`.
- `models.py`: the dataclasses below, plus `format_bytes()` (gives `1.50 KiB`, `None` gives `N/A`).
- `base.py`: `BaseMonitoring`, the base class every monitor subclasses.
- `utils.py`: the older `format_bytes()` (gives `1.5 KB`).

Rates need two readings. The first `collect_all()` call returns `None` for every rate. `collect_by_id()` also counts as a reading.

```
InterfaceStats
    name, is_up
    duplex          "NIC_DUPLEX_FULL" / "NIC_DUPLEX_HALF" / "NIC_DUPLEX_UNKNOWN"
    speed           Mb/s, 0 if unknown (loopback, Wi-Fi)
    mtu             bytes
    flags           e.g. "up,broadcast,running,multicast"
    network_info    NetworkInfo
    packets_sent, packets_recv, bytes_sent, bytes_recv    totals
    errin, errout, dropin, dropout                        totals
    traffic_rates   TrafficRates

TrafficRates        None until the second reading
    tx_packet_rate, rx_packet_rate    packets/s
    tx_byte_rate, rx_byte_rate        bytes/s

NetworkInfo
    addresses       list of NetworkAddress (IPv4, IPv6, MAC)
    gateway         not implemented yet, always None
    .ipv4, .ipv6    addresses filtered by family

NetworkAddress
    family, address, netmask, broadcast, ptp
```

**To add a new tab**, for example a Connections tab:

1. In `services/`, create a class that subclasses `BaseMonitoring` (from `services/network/base.py`) and implements `collect_all()` and `collect_by_id()`.
2. In `ui/`, create a widget that displays that data.
3. In `app.py`, add one line inside `MainWindow`: `self.tabs.addTab(YourView(YourMonitor()), "Your tab name")`.
