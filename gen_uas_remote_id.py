#!/usr/bin/env python3

# Copyright Michael Platzer
# Licensed under the ISC license, see LICENSE.txt for details
# SPDX-License-Identifier: ISC

import argparse
import struct
import subprocess
import signal
import time

parser = argparse.ArgumentParser(description='Generate UAS remote ID beacons')
parser.add_argument('-i', '--interface', metavar='INTERFACE', default='wlan0',
                    help='Wireless interface to be used for the AP')
parser.add_argument('-s', '--ssid', metavar='SSID', default='test',
                    help='SSID to be used in IEEE 802.11 management frames')
parser.add_argument('start', metavar="LONG,LAT,ALT",
                    help='Start position given by longitude (in degrees), '
                         'latitude (in degrees) and altitude (in meters) '
                         'within the WGS84 (EPSG 4326) reference system')
args = parser.parse_args()

start_pos = [float(val) for val in args.start.split(',')]


def uas_id_payload(uas_id, pos, alt, height, speed, course, home):
    # format the UAS remote ID payload according to french regulation:
    # https://www.legifrance.gouv.fr/eli/arrete/2019/12/27/ECOI1934044A/jo/texte

    pos  = (pos [0] * 10000, pos [1] * 10000)
    home = (home[0] * 10000, home[1] * 10000)
    payload = bytearray([
        0x6a, 0x5c, 0x35,   # OUI
        0x01                # VS types
    ])
    # TODO verify byte order (using big endian for now)
    for dtype, vformat, val in [
        (1 , '>B', 1           ), # protocol version (8-bit unsigned)
        (2 , None, uas_id      ), # UAS ID
        (4 , '>l', int(pos[1] )), # current latitude  (32-bit signed)
        (5 , '>l', int(pos[0] )), # current longitude (32-bit signed)
        (6 , '>h', int(alt    )), # current altitude  (16-bit signed)
        (7 , '>h', int(height )), # height above take-off point (16-bit signed)
        (8 , '>l', int(home[1])), # latitude of take-off point  (32-bit signed)
        (9 , '>l', int(home[0])), # longitude of take-off point (32-bit signed)
        (10, '>B', int(speed  )), # ground speed (8-bit unsigned)
        (11, '>H', int(course ))  # course (16-bit unsigned)
    ]:
        if val is not None:
            bvalues  = val if vformat is None else struct.pack(vformat, val)
            payload += bytearray([dtype, len(bvalues)]) + bvalues
    return bytearray([0xdd, len(payload)]) + payload


dynamic_ap = subprocess.Popen([
    '/usr/bin/env', 'python3', 'dynamic_hostapd.py',
    '-i', args.interface,
    '-s', args.ssid,
    '-c', 'hostapd.conf',
    'beacon'
], stdin=subprocess.PIPE)

home     = (start_pos[0], start_pos[1])
home_alt = start_pos[2]
pos      = home
alt      = home_alt
height   = 0.
speed    = 0.
course   = 0.

try:
    while True:
        data = uas_id_payload(bytes(30), pos, alt, height, speed, course, home)
        dynamic_ap.stdin.write(data.hex().encode() + b'\n')
        time.sleep(0.2)

        pos    = (pos[0] + 0.00001, pos[1] + 0.00001)
        height = height + 0.1
        alt    = home_alt + height
        speed  = 3.
        course = 45.
except:
    dynamic_ap.send_signal(signal.SIGINT)
    raise
