# Remote identification for UAS using WiFi beacon frames


## Raspberry Pi Quick Setup

First, clone this repository and install `hostapd`.

```
$ git clone https://github.com/michael-platzer/uas-remote-id.git
# apt install hostapd
```

Next, make sure that WiFi is not blocked by rfkill (which is the default on a
fresh install of Raspi OS).  Note that this setting is restored at boot time.

```
# rfkill unblock wlan
```

Run the `gen_uas_remote_id.py` script to start generating test beacon frames.

```
# ./gen_uas_remote_id.py [-i INTERFACE] [-s SSID] LONG,LAT,ALT
```

The option `-i` allows to specify the WiFi interface to use (use `iw dev` to
show all available WiFi interfaces) and `-s` allows to specify an SSID name to
be used in the beacon frames.  `LONG`, `LAT`, and `ALT` are the longitude,
latitude, and altitude, respectively, of the desired start point in WGS84
(EPSG 4326) coordinates.

Example use:

```
# ./gen_uas_remote_id.py -i wlan0 -s Test 13.5,47,200.5
```


## Verifying with Wireshark

In order to verify whether the beacon frames are correctly generated, create a
monitor for WiFi frames on a separate machine and use Wireshark to capture
frames.

```
# systemctl stop NetworkManager
# iw dev <wlan-interface> interface add mon0 type monitor
# ip link set mon0 up
```

Within Wireshark, open the monitor interface `mon0` for capturing.  In order to
filter only beacon frames, use the `wlan.fc.type_subtype == 0x0008` filter
rule.
