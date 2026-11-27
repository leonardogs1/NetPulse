# psutil Module
-------------------
psutil is a python package that retrieves information on ongoing processes and system usage (CPU, memory, network, and sensors). Its mainly used for system monitoring, profiling, restricting process resources, and process management.


# Methods
------------

## `net_io_counters()`

**Description:** Returns the system wide network input/output statistics in the form of counters as tuple. The difference counters returned are as follows:

**Arguments:**
- `pernic` (`bool`): Returns statistics per interface when True.
- `nowrap` (`bool`): Handles counter overflow.

**Returns:** `snetio` or `dict[str, snetio]`

**Return Fields:**
- `bytes_sent` (`int`): Total bytes transmitted.
- `bytes_recv` (`int`): Total bytes received.
- `packets_sent` (`int`): Total packets transmitted.
- `packets_recv` (`int`): Total packets received.
- `errin` (`int`): Incoming packet errors.
- `errout` (`int`): Outgoing packet errors.
- `dropin` (`int`): Incoming packets dropped.
- `dropout` (`int`): Outgoing packets dropped. 

**Implementation:**
- Two approaches to calcualte data transfer:
    - PREFERRED: Measure actual time lapsed using time.monotonic
    - Secondary: Measure bytes trasferred during an interval
**Notes:**
- Returned counters are cumulative values (though counter can be reseted)


```
psutil.net_io_counters()
snetio(bytes_sent=14508483, bytes_recv=62749361, packets_sent=84311, packets_recv=94888, errin=0, errout=0, dropin=0, dropout=0)
>>>
>>> psutil.net_io_counters(pernic=True)
{'lo': snetio(bytes_sent=547971, bytes_recv=547971, packets_sent=5075, packets_recv=5075, errin=0, errout=0, dropin=0, dropout=0),
'wlan0': snetio(bytes_sent=13921765, bytes_recv=62162574, packets_sent=79097, packets_recv=89648, errin=0, errout=0, dropin=0, dropout=0)}
```

## `net_if_addrs()`

**Description:** Returns the addresses associated to each NIC installed on the system as a dict whost keys are the NICs names and value is a list of tuples for each address assigned to the NIC. Each named tuple includes 5 fields: 

- `family` the address family, either AF_INET or AF_INET6 or psutil.AF_LINK, which refers to a mac address
- `address` (`string`): The primary NIC address (always set)
- `netmask` (`string`): subnet mask
- `broadcast` (`string`): Broadcast address
- `ptp` (`string`): It's destination address on a p2p interface

broadast and ptp are mutally exclusive and may be None

```
>>> psutil.net_if_addrs()
{'lo': [snicaddr(family=<AddressFamily.AF_INET: 2>, address='127.0.0.1', netmask='255.0.0.0', broadcast='127.0.0.1', ptp=None),
        snicaddr(family=<AddressFamily.AF_INET6: 10>, address='::1', netmask='ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff', broadcast=None, ptp=None),
        snicaddr(family=<AddressFamily.AF_LINK: 17>, address='00:00:00:00:00:00', netmask=None, broadcast='00:00:00:00:00:00', ptp=None)],
 'wlan0': [snicaddr(family=<AddressFamily.AF_INET: 2>, address='192.168.1.3', netmask='255.255.255.0', broadcast='192.168.1.255', ptp=None),
           snicaddr(family=<AddressFamily.AF_INET6: 10>, address='fe80::c685:8ff:fe45:641%wlan0', netmask='ffff:ffff:ffff:ffff::', broadcast=None, ptp=None),
           snicaddr(family=<AddressFamily.AF_LINK: 17>, address='c4:85:08:45:06:41', netmask=None, broadcast='ff:ff:ff:ff:ff:ff', ptp=None)]}
```


## `net_if_stats()

**Description:** Return information about each NIC (network interface card) installed on the system as a dictionary whose keys are the NIC names and value is a named tuple with the following fields:
- `isup` a bool indicating whether the NIC is up and running (meaning ethernet cable or Wi-Fi is connected)
- `duplex` the duplex communication type; it can be either NIC_DUPLEX_FULL, NIC_DUPLEX_HALF or NIC_DUPLEX_UNKNOWN
- `speed` the NIC speed expressed in mega bits (MB), if it can’t be determined (e.g. ‘localhost’) it will be set to 0
-` mtu` NIC’s maximum transmission unit expressed in bytes
- `flags`  a string of comma-separated flags on the interface (may be an empty string). Possible flags are: up, broadcast, debug, loopback, pointopoint, notrailers, running, noarp, promisc, allmulti, master, slave, multicast, portsel, dynamic, oactive, simplex, link0, link1, link2, and d2 (some flags are only available on certain platforms)
