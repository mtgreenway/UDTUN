#! /usr/bin/env python
#  Copyright 2013 Matt Greenway LAC
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

"""
UDTCAT POC. adapted from:
    http://www.secdev.org/projects/tuntap_udp/files/tunproxy.py

to run:
    # "server"
    $ mkfifo pipe
    $ sudo ./tun.py 10.0.0.1/24 < pipe|uc -l 9000 > pipe

    # "client"
    $ mkfifo pipe
    $ sudo ./tun.py 10.0.0.2/24 < pipe|uc server.host.name 9000 > pipe
    $ rsync 10.0.0.1::

where uc is UDTCAT https://github.com/millerjs/UDTCAT
"""

import os
import sys
from subprocess import call
from fcntl import ioctl
from select import select
import struct

buf_size = 67108864

TUNSETIFF = 0x400454ca
TUNMODE = 0x0001

f = os.open("/dev/net/tun", os.O_RDWR)
ifs = ioctl(f, TUNSETIFF, struct.pack("16sH", "tun%d", TUNMODE))
ifname = ifs[:16].strip("\x00")

ip = sys.argv[1]
call("ip addr add %s dev %s" % (ip, ifname), shell=True)
call("ip link set %s up" % ifname, shell=True)
call("ip link set %s mtu 7500" % ifname, shell=True)
call("ip link set %s txqueuelen 10000" % ifname, shell=True)

while 1:
    r = select([f, 0],[],[])[0][0]
    if r == f:
        os.write(1, os.read(f,buf_size))
    else:
        os.write(f, os.read(0,buf_size))
