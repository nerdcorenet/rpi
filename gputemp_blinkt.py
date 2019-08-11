#!/usr/bin/env python
#
# gputemp_blinkt.py - Show remote GPU temperatures on a Blinkt!
#
# I run this on the remote server:
#   nvidia-smi -l 1 --format=csv,noheader --query-gpu=index,temperature.gpu | nc -l <port>
#
# Copyright (c) 2019 Mike Mallett <mike@nerdcore.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import blinkt

import socket

# Put your connection details here
ip = ""
port = ""

# show temp t on led l
def show_temp(l,t):
    r=0;g=0;b=0
    # Cold white-blue
    if 0 <= t < 21:
        b=255
        g=int(255-(t*255/20))
        r=int(255-(t*255/20))
    # Idle blue-green
    if 20 < t < 41:
        b=int(255-((t-20)*255/20))
        g=int((t-20)*255/20)
    # Warm green-yellow
    if 40 < t < 61:
        r=int((t-40)*127/20)
        g=int(255-((t-40)*127/20))
    # Warm yellow-orange
    if 60 < t < 81:
        r=int(127+((t-60)*127/20))
        g=int(127-((t-60)*64/20))
    # Hot orange-red
    if t > 80:
        g=int(64-((t-80)*64/10))
        r=255
    print('gpu:{} temp:{} r:{} g:{} b:{}').format(l, t, r, g, b)
    blinkt.set_pixel(l, r, g, b)
    blinkt.show()

blinkt.set_clear_on_exit()
blinkt.set_brightness(0.1)
blinkt.clear()

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print "Socket successfully created"
except socket.error as err:
    print "socket creation failed with error %s" %(err)

s.connect((ip, port))
# Socket as File gives us buffered readline()
sf = s.makefile()

while True:
    temps_recv = sf.readline()
    l = temps_recv.split(", ")
    gpu = int(l[0])
    temp = int(l[1])
    show_temp(gpu, temp)

print "Flagrant System Error!"
blinkt.clear()
