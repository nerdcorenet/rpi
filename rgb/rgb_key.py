#!/usr/bin/env python3
#
# A key-controlled utility for turning three LEDs on/off
#
# Copyright (c) 2020 Mike Mallett <mike@nerdcore.net>
#
# THIS SOFTWARE IS PROVIDED AS-IS WITHOUT ANY WARRANTY NOT EVEN THE
# WARRANTY OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE. IN
# NO WAY SHALL MIKE MALLETT BE HELD LIABLE FOR ANY DAMAGAES BE THEY
# DIRECT, INDIRECT, CONSEQUENTIAL, INCONSEQUENTIAL, INTENTIONAL,
# UNINTENTIONAL, POSSIBLE, IMPOSSIBLE, INCIDENTAL, DENTAL,
# PREMEDITATED, MEDITATED, MEDICATED, POST-DOCTRINATED, PASSIVE,
# ACTIVE, KNOWN, UNKNOWN, FLIPPANT, ACT OF GOD, OR ANY OTHER REASONS
# WHATSOEVER TO THE MAXIMUM EXTENT ALLOWABLE BY LAW.

#### IMPORTS ####
import RPi.GPIO as GPIO
import time
import math

#### SETUP ####

# Set these to your own configuration
GPIO.setmode(GPIO.BCM)
PIN_R=14
PIN_G=15
PIN_B=18

GPIO.setwarnings(False)

GPIO.setup(PIN_R, GPIO.OUT)
GPIO.setup(PIN_G, GPIO.OUT)
GPIO.setup(PIN_B, GPIO.OUT)

GPIO.output(PIN_R, 0)
GPIO.output(PIN_G, 0)
GPIO.output(PIN_B, 0)

#### DEFINES ####
def getch():
  import sys, tty, termios, os
  old_settings = termios.tcgetattr(0)
  new_settings = old_settings[:]
  new_settings[3] &= ~termios.ICANON
  try:
    termios.tcsetattr(0, termios.TCSANOW, new_settings)
    os.system("stty -echo")
    ch = sys.stdin.read(1)
    os.system("stty echo")
  finally:
    termios.tcsetattr(0, termios.TCSANOW, old_settings)
  return ch

def main_loop():
  ron=0
  gon=0
  bon=0
  while 1:
    c = getch()
    if (c=='r'):
      ron = invert(ron)
      do_rgb(ron, gon, bon)
    if (c=='b'):
      bon = invert(bon)
      do_rgb(ron, gon, bon)
    if (c=='g'):
      gon = invert(gon)
      do_rgb(ron, gon, bon)
    if (c=='q' or c=='x'):
      leave()

def invert(x):
  return 0 if x else 1

def print_colour(r, g, b):
  red = "\033[1;31mRed"
  green = "\033[1;32mGreen"
  blue = "\033[1;34mBlue"
  magenta = "\033[1;35mMagenta"
  cyan = "\033[1;36mCyan"
  yellow = "\033[1;33mYellow"
  white = "\033[1;37mWhite"
  off = "\033[0m(Off)"

  if (r==0 and g==0 and b==0):
    print(off)
  if (r==1 and g==0 and b==0):
    print(red)
  if (r==0 and g==1 and b==0):
    print(green)
  if (r==0 and g==0 and b==1):
    print(blue)
  if (r==0 and g==1 and b==1):
    print(cyan)
  if (r==1 and g==0 and b==1):
    print(magenta)
  if (r==1 and g==1 and b==0):
    print(yellow)
  if (r==1 and g==1 and b==1):
    print(white)

# Set RGB LEDs on/off each, and print colour to console
def do_rgb(r, g, b):
  GPIO.output(PIN_R, r)
  GPIO.output(PIN_G, g)
  GPIO.output(PIN_B, b)
  # DEBUG
  print_colour(r, g, b)

# Fancy exit
def leave(msg=''):
  if (msg != ''):
    print(msg)
  GPIO.cleanup()
  exit()

#### MAIN ####
if __name__ == '__main__':
  try:
    print("Press 'r' for Red, 'g' for Green, 'b' for Blue, 'q' or 'x' to exit.")
    main_loop()
  except KeyboardInterrupt:
    pass
  finally:
    leave()
