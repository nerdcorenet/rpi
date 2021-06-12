#!/usr/bin/python
#
# This is based off Leon Anavi's repository
#   https://github.com/leon-anavi/raspberrypi-lcd
#
# Copyright 2015 Matt Hawkins, Leon Anavi
#
# with additions by nerdcorenet
#
# Copyright (c) 2019 Mike Mallett <mike@nerdcore.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
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

# Here are some datasheets which might be helpful:
# https://cdn-shop.adafruit.com/datasheets/TC1602A-01T.pdf
# https://components101.com/sites/default/files/component_datasheet/16x2%20LCD%20Datasheet.pdf

# The wiring for the LCD is as follows:
# 1 : GND
# 2 : 5V
# 3 : Contrast (0-5V)*
# 4 : RS (Register Select)
# 5 : R/W (Read Write)       - GROUND THIS PIN
# 6 : Enable or Strobe
# 7 : Data Bit 0             - NOT USED
# 8 : Data Bit 1             - NOT USED
# 9 : Data Bit 2             - NOT USED
# 10: Data Bit 3             - NOT USED
# 11: Data Bit 4
# 12: Data Bit 5
# 13: Data Bit 6
# 14: Data Bit 7
# 15: LCD Backlight +5V**
# 16: LCD Backlight GND

# 00000001 = Clear
# 00110011 = Initialise
# 00110010 = Initialise
# 000110 Cursor move direction
# 001100 Display On,Cursor Off, Blink Off
# 001111 Display On,Cursor On, Blink On
# 101000 Data length, number of lines, font size

# Important command codes for LCD:
# Hex  Binary  Command to LCD instruction Register
# --- -------- -----------------------------------
# 01  00000001 Clear display screen
# 02  00000010 Return home
# 04  00000100 Decrement cursor (shift cursor to left)
# 06  00000110 Increment cursor (shift cursor to right)
# 05  00000101 Shift display right
# 07  00000111 Shift display left
# 08  00001000 Display off, cursor off
# 0A  00001010 Display off, cursor on
# 0C  00001100 Display on, cursor off
# 0E  00001110 Display on, cursor blinking
# 0F  00001111 Display on, cursor blinking
# 10  00010000 Shift cursor position to left
# 14  00010100 Shift cursor position to right
# 18  00011000 Shift the entire display to the left
# 1C  00011100 Shift the entire display to the right
# 22  00100010 Initialize 4-bit mode
# 80  10000000 Force cursor to beginning ( 1st line)
# C0  11000000 Force cursor to beginning ( 2nd line)
# 38  00111000 2 lines and 5x7 matrix

import RPi.GPIO as GPIO
#import struct
import time
import requests
#from time import localtime, strftime

# a = "base"
# b = "target"
# d = digits of precision (right of ".")
def cryptoprice(a, b, d=8):
  # https://api.cryptonator.com/api/ticker/a-b
  price_url = "https://api.cryptonator.com/api/ticker/" + a + "-" + b
  # ClourFlare requires a User-Agent header, otherwise returns 502 error
  # https://stackoverflow.com/questions/43616566/python-requests-response-520/43616647#43616647
  price_result = requests.get(price_url, headers={'User-Agent': 'lcd.py'})
  price_json = price_result.json()
  price = float(price_json["ticker"]["price"])
  # Truncate to precision d
  precision = "." + str(d) + "f"
  #p = str(int(price * precision) / float(precision))
  return format(price, precision)

# Define GPIO to LCD mapping
LCD_RS = 7
LCD_E  = 8
LCD_D4 = 25
LCD_D5 = 24
LCD_D6 = 23
LCD_D7 = 18


# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

# API rate limiter
API_RATE = 4500

def main():
  # Main program block
  
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
  GPIO.setup(LCD_E, GPIO.OUT)  # E
  GPIO.setup(LCD_RS, GPIO.OUT) # RS
  GPIO.setup(LCD_D4, GPIO.OUT) # DB4
  GPIO.setup(LCD_D5, GPIO.OUT) # DB5
  GPIO.setup(LCD_D6, GPIO.OUT) # DB6
  GPIO.setup(LCD_D7, GPIO.OUT) # DB7

  # Initialise display
  lcd_init()

  # Get prices
  # TODO: Loop this, and observe API_RATE limit
  btcusd = cryptoprice("BTC", "USD", 2)
  btccad = cryptoprice("BTC", "CAD", 2)
  ltcbtc = cryptoprice("LTC", "BTC")
  ethbtc = cryptoprice("ETH", "BTC")
  xmrbtc = cryptoprice("XMR", "BTC")
  dogebtc = cryptoprice("DOGE", "BTC")

  while True:
    lcd_string("BTC-USD", LCD_LINE_1)
    lcd_string(btcusd, LCD_LINE_2)
    time.sleep(3)
    lcd_string("BTC-CAD", LCD_LINE_1)
    lcd_string(btccad, LCD_LINE_2)
    time.sleep(3)
    lcd_string("LTC-BTC", LCD_LINE_1)
    lcd_string(ltcbtc, LCD_LINE_2)
    time.sleep(3)
    lcd_string("ETH-BTC", LCD_LINE_1)
    lcd_string(ethbtc, LCD_LINE_2)
    time.sleep(3)
    lcd_string("XMR-BTC", LCD_LINE_1)
    lcd_string(xmrbtc, LCD_LINE_2)
    time.sleep(3)
    lcd_string("DOGE-BTC", LCD_LINE_1)
    lcd_string(dogebtc, LCD_LINE_2)
    time.sleep(3)

def lcd_init():
  # Initialise display
#  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
#  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x22,LCD_CMD) # 100010 Initialise 4-bit mode
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  #lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x0F,LCD_CMD) # 001111 Display On,Cursor On, Blink On
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command

  GPIO.output(LCD_RS, mode) # RS

  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

def lcd_toggle_enable():
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)

def lcd_string(message,line):
  # Cast to string
  message = str(message)
  # Send string to display
  message = message.ljust(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

  # TESTING
  # Scroll text (there and back again...)
#  for i in range(LCD_WIDTH):
#    lcd_byte(0x1C, LCD_CMD)
#    time.sleep(0.1)
#  for i in range(LCD_WIDTH):
#    lcd_byte(0x1B, LCD_CMD)
#    time.sleep(0.1)

if __name__ == '__main__':

  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)
    lcd_string("Goodbye!",LCD_LINE_1)
    GPIO.cleanup()
