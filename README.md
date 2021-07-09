# Remote identification for UAS using WiFi beacon frames

## Run an AP with dynamically updated IEEE 802.11 beacon frames

## Verifying with Wireshark

```
# systemctl stop NetworkManager
# iw dev <wlan-interface> interface add mon0 type monitor
# ip link set mon0 up
```
