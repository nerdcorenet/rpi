#!/usr/bin/env python3
#
# shiftreg-count.py: Binary counter for 74HC595 shift register
#
# Copyright (c) 2020 Mike Mallett <mike@nerdcore.net>
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

# This code drives a 74HC595 8-bit shift register:
#
#         +-----+
#  BIT_1 -|  U  |- VCC (+5V)
#  BIT_2 -|     |- BIT_0
#  BIT_3 -|     |- DS "Data Serial"
#  BIT_4 -|     |- CE
#  BIT_5 -|     |- ST "Store"
#  BIT_6 -|     |- SH "Shift"
#  BIT_7 -|     |- MR
#  -/GND -|     |- BIT_7'
#         +-----+

import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)

# https://www.ti.com/lit/ds/symlink/sn74hc595.pdf
# At 25C ambient temp and 4.5V, minimum pulse is 20ns
PULSE=30 / 1000000000
#PULSE=0.01

# You should change these to match your setup
GPIO.setmode(GPIO.BCM)
PIN_DATA=17  # DS "Data Serial"
PIN_STORE=27 # SH "Shift"
PIN_OUT=18   # ST "Store"
PAUSE=0.1

GPIO.setup(PIN_DATA, GPIO.OUT)
GPIO.setup(PIN_STORE, GPIO.OUT)
GPIO.setup(PIN_OUT, GPIO.OUT)
# Clear all pins
GPIO.output(PIN_DATA, 0)
GPIO.output(PIN_STORE, 0)
GPIO.output(PIN_OUT, 0)

# Push the low 8 bits of the given integer to the register
# If you have reversed your output pins, change the if to:
#   if (i & (7-(2**bit))):
def int2reg(i):
    for bit in range(8):
        if (i & (2**bit)): # Backwards??
            GPIO.output(PIN_DATA, 1)
        else:
            GPIO.output(PIN_DATA, 0)
        pulse(PIN_STORE)
    pulse(PIN_OUT)

def pulse(pin):
    GPIO.output(pin, 0)
    time.sleep(PULSE)
    GPIO.output(pin, 1)
    time.sleep(PULSE)
    GPIO.output(pin, 0)
    time.sleep(PULSE)

def count():
    while 1:
        for x in range(256):
            int2reg(x)
            time.sleep(PAUSE)

if __name__ == '__main__':
  try:
    count()
  except KeyboardInterrupt:
    pass
  finally:
    int2reg(0)
    GPIO.cleanup()
