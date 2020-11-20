#!/usr/bin/env python3

#### IMPORTS ####
import RPi.GPIO as GPIO
import time
import math

#### SETUP ####
GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)

PIN_R=14
PIN_G=15
PIN_B=18
PWM_FREQ=2000

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
    if (c=='b'):
      bon = invert(bon)
    if (c=='g'):
      gon = invert(gon)
    GPIO.output(PIN_R, ron)
    GPIO.output(PIN_G, gon)
    GPIO.output(PIN_B, bon)
    # DEBUG
    print_colour(ron, gon, bon)

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

#### MAIN ####
if __name__ == '__main__':
  try:
    main_loop()
  except KeyboardInterrupt:
    pass
  finally:
    GPIO.cleanup()
