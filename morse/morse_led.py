#!/usr/bin/env python
#
# A script to blink morse code to a LED on a GPIO pin.
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
#

from gpiozero import LED
import time
import fileinput

#########
# NOTES #
#########
# The duration of a Dot is considered one time unit.
# The duration of a Dash is three time units.
# The duration of the gap between elemnts of a letter is one time unit.
# The duration of the gap between letters in a word is three time units.
# The duration of the gap between words is seven time units.
#
# https://gpiozero.readthedocs.io/en/stable/api_output.html
# https://www.geeksforgeeks.org/morse-code-translator-python/

#########
# SETUP #
#########
# Set this to the correct GPIO pin for your setup
PIN=15
# Set this to your desired time unit length in seconds
PULSE=0.1
# These are derived from that
DOT=PULSE
DASH=PULSE*3
# We reduce these delays by one unit, because each . or - being
# output will also be followed by a one unit delay in the loop
LETTER=PULSE*2
WORD=PULSE*6

out = LED(PIN)

# Dictionary representing the morse code chart
# Expand as desired
MORSE_CODE_DICT = { 'A':'.-', 'B':'-...',
                    'C':'-.-.', 'D':'-..', 'E':'.',
                    'F':'..-.', 'G':'--.', 'H':'....',
                    'I':'..', 'J':'.---', 'K':'-.-',
                    'L':'.-..', 'M':'--', 'N':'-.',
                    'O':'---', 'P':'.--.', 'Q':'--.-',
                    'R':'.-.', 'S':'...', 'T':'-',
                    'U':'..-', 'V':'...-', 'W':'.--',
                    'X':'-..-', 'Y':'-.--', 'Z':'--..',
                    '1':'.----', '2':'..---', '3':'...--',
                    '4':'....-', '5':'.....', '6':'-....',
                    '7':'--...', '8':'---..', '9':'----.',
                    '0':'-----', ',':'--..--', '.':'.-.-.-',
                    '?':'..--..', '/':'-..-.', '-':'-....-',
                    '(':'-.--.', ')':'-.--.-'}
MORSE_CODE_CHARS = MORSE_CODE_DICT.keys()

def morsify(msg):
  for symbol in msg.upper():
    if symbol == ' ':
      time.sleep(WORD)
      continue
    if symbol not in MORSE_CODE_CHARS:
      print("Unrecognized character: " + symbol)
      continue
    for d in MORSE_CODE_DICT[symbol]:
      if d == '.':
        out.blink(DOT, PULSE, 1, False)
      if d == '-':
        out.blink(DASH, PULSE, 1, False)
    time.sleep(LETTER)

def main():
  for line in fileinput.input():
    morsify(line)

# Executes the main function
if __name__ == '__main__':
  main()
