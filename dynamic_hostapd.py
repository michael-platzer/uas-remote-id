#!/usr/bin/env python3

# Copyright Michael Platzer
# Licensed under the ISC license, see LICENSE.txt for details
# SPDX-License-Identifier: ISC

import argparse
import sys
import subprocess
import signal

parser = argparse.ArgumentParser(description='Dynamically update hostapd.conf')
parser.add_argument('-i', '--interface', metavar='INTERFACE', default='wlan0',
                    help='Wireless interface to be used for the AP')
parser.add_argument('-s', '--ssid', metavar='SSID', default='test',
                    help='SSID to be used in IEEE 802.11 management frames')
parser.add_argument('-c', '--conf', metavar='hostapd.conf',
                    default='/etc/hostapd/hostapd.conf',
                    help='Alternative location for hostapd.conf file')
parser.add_argument('-d', '--debug', action='store_true',
                    help='Print debug info')
parser.add_argument('mode', metavar="MODE",
                    help='Beacon mode: transmit beacons with additional '
                         'information sent in the vendor specific payload '
                         'field; that additional information is read from '
                         'stdin as a hexdump of the raw content (including '
                         'id+len+payload); everytime a new line is read from '
                         'stdin that information is updated dynamically.')
args = parser.parse_args()


def gen_hostapd_conf(vendor_elems):
    # ref: https://unix.stackexchange.com/a/334005/49250
    with open(args.conf, 'w') as conf:
        conf.write('##### hostapd configuration file #####\n')
        conf.write('\n')
        conf.write('# AP netdevice name\n')
        conf.write(f"interface={args.interface}\n")
        conf.write('\n')
        conf.write('\n')
        conf.write('##### IEEE 802.11 related configuration #####\n')
        conf.write('\n')
        conf.write('# SSID to be used in IEEE 802.11 management frames\n')
        conf.write(f"ssid={args.ssid}\n")
        conf.write('\n')
        conf.write('# Operation mode\n')
        conf.write('hw_mode=g\n')
        conf.write('\n')
        conf.write('# Channel number (IEEE 802.11)\n')
        conf.write('channel=1\n')
        conf.write('\n')
        conf.write('# Beacon interval in kus (1.024 ms) (default: 100)\n')
        conf.write('beacon_int=100\n')
        conf.write('\n')
        conf.write('# DTIM (delivery traffic information message) period\n')
        conf.write('dtim_period=2\n')
        conf.write('\n')
        conf.write('# Maximum number of stations allowed in station table\n')
        conf.write('max_num_sta=255\n')
        conf.write('\n')
        conf.write('# Additional vendor specific elements\n')
        if vendor_elems is None:
            conf.write('#vendor_elements=dd0411223301\n')
        else:
            conf.write(f"vendor_elements={vendor_elems}\n")
        conf.write('\n')
        conf.write('# Use WPA2\n')
        conf.write('wpa=2\n')
        conf.write('\n')
        conf.write('# Set WPA2 password\n')
        conf.write('wpa_passphrase=c3b34bf61d9c061c0417f7ab8a49480f\n')
        conf.write('\n')


hostapd = None

try:
    for line in sys.stdin:
        gen_hostapd_conf(line.strip(' \n'))

        # start hostapd or trigger reconfiguration in case it already runs
        # http://lists.infradead.org/pipermail/hostap/2017-October/038000.html
        if hostapd is None:
            arguments = (['-dd'] if args.debug else []) + [args.conf]
            hostapd   = subprocess.Popen(['hostapd'] + arguments)
        else:
            hostapd.send_signal(signal.SIGHUP)
except:
    hostapd.send_signal(signal.SIGINT)
    raise
