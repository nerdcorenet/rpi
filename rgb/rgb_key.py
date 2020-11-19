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
  import sys, tty, termios
  old_settings = termios.tcgetattr(0)
  new_settings = old_settings[:]
  new_settings[3] &= ~termios.ICANON
  try:
    termios.tcsetattr(0, termios.TCSANOW, new_settings)
    ch = sys.stdin.read(1)
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

def invert(x):
  if (x==0):
    return 1
  else:
    return 0

#### MAIN ####
if __name__ == '__main__':
  try:
    main_loop()
  except KeyboardInterrupt:
    pass
  finally:
    GPIO.cleanup()
