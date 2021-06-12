#!/usr/bin/env python3
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
# 0E  00001110 Display on, cursor not blinking
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
import time
import requests

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
LCD_BUFFER = 0x27 # Per-line character buffer width

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005
SCROLL_DELAY = 0.8

# API rate limiter (seconds)
API_RATE = 300

class Currency:
  def __init__(self,code):
    self.code = code
    # Precisions from ISO 4217 and other resources
    # Dollars from https://en.wikipedia.org/wiki/Dollar
    # Other cryptocurrencies have other specific denominations/precision
    if code in ["AUD","BBD","MD","BND","BSD","BZD","CAD","FJD","GYD","HKD","JMD","KYD","LRD","NZD","SBD","SGD","TTD","TVD","TWD","USD","XCD"]:
      self.precision = 2 # Cent
      self.symbol = 0x24 # Dollar
    elif code in ["EUR"]:
      self.precision = 2
      self.symbol = 0x06 # Euro
    elif code in ["EGP","FKP","GIP","GBP","SHP","SSP","SYP"]:
      self.precision = 2
      self.symbol = 0x07
    elif code in ["JPY"]:
      self.precision = 0
      self.symbol = 0x5C
    elif code in ["CNY"]:
      self.precision = 2
      self.symbol = 0x5C
    elif code in ["AED","AFN","ALL","AMD","AOA","ARS","AWG","AZN","BAM","BDT","BGN","BOB","BRL","BTN","BWP","BYN","CDF","CHF","COP","CRC","CUP","CVE","CZK","DKK","DOP","DZD","ERN","ETB","GEL","GHS","GMD","GTQ","HNL","HRK","HTG","HUF","IDR","ILS","INR","IRR","KES","KGS","KHR","KPW","KZT","LAK","LBP","LKR","LSL","MAD","MDL","MGA","MKD","MMK","MNT","MOP","MRU","MUR","MVR","MWK","MXN","MYR","MZN","NAD","NGN","NIO","NOK","NPR","PAB","PEN","PGK","PHP","PKR","PLN","QAR","RON","RSD","RUB","SAR","SCR","SDG","SEK","SLL","SOS","SRD","STN","SZL","THB","TJS","TMT","TOP","TRY","TZS","UAH","UYU","UZS","VEF","WST","YER","ZAR","ZMW","ZWL"]:
      self.precision = 2
      self.symbol = 0xFE # null
    elif code in ["BIF","CLP","DJF","GNF","ISK","KMF","KRW","PYG","RWF","UGX","VND","VUV","XAF","XPF"]:
      self.precision = 0
      self.symbol = 0xFE
    elif code in ["BHD","IQD","JOD","KWD","LYD","OMR","TND"]:
      self.precision = 3
      self.symbol = 0xFE
    elif code in ["BTC","BCH","BSV","BTG"]:
      self.precision = 8 # Satoshi
      self.symbol = 0x02 # Bitcoin
    elif code in ["XMR"]:
      self.precision = 12 # Picomonero
      self.symbol = 0x05 # Monero
    elif code in ["ETH","ETC"]:
      self.precision = 18 # Wei
      self.symbol = 0x03 # Ethereum
    elif code in ["DOGE"]:
      self.precision = 8
      self.symbol = 0x04
    else:
      self.precision=8
      self.symbol = 0xFE

class Price:
  def __init__(self,base,target):
    self.base=Currency(base)
    self.target=Currency(target)
    self.precision=self.target.precision
    self.symbol=self.target.symbol
    self.value=0.0
    #self.old=0.0
    #self.update()

  def __str__(self):
    self.pair()

  # Return the name of the trade pair "base-target"
  def pair(self):
    return self.base.code + "-" + self.target.code
  # Return a nicely formatted value
  def show(self):
    ret = "" if self.symbol==0xFE else chr(self.symbol)
    if self.precision==0:
      return ret + format(int(self.value), "d")
    return ret + format(self.value, "."+str(self.precision)+"f")

  def update(self):
    self.old = self.value
    price_url = "https://api.cryptonator.com/api/ticker/" + self.pair()
    # ClourFlare requires a User-Agent header, otherwise returns 502 error
    # https://stackoverflow.com/questions/43616566/python-requests-response-520/43616647#43616647
    price_result = requests.get(price_url, headers={'User-Agent': 'lcd.py'})
    price_json = price_result.json()
    self.value = float(price_json["ticker"]["price"])
    # DEBUG
    print("Got " + self.pair() + ": " + self.show())
    return self.value

def prices_show(prices):
  for pair in list(prices.keys()):
    lcd_string(pair, LCD_LINE_1)
    lcd_string(prices[pair], LCD_LINE_2)
    time.sleep(3)

def prices_scroll(prices, col = LCD_WIDTH):
  # DEBUG
  print("COL | ADR1 | CH1 | ADR2 | CH2")

  # Show prices
  for price in prices:
    if price.old!=0 and price.value > price.old:
      pair_str = chr(0x00) + price.pair()
    elif price.old!=0 and price.value < price.old:
      pair_str = chr(0x01) + price.pair()
    else:
      #pair_str = "=" + price.pair()
      pair_str = price.pair()

    num_chars = (len(pair_str) if (len(pair_str) > len(price.show())) else len(price.show())) + 2
    pair_str = pair_str.ljust(num_chars)
    price_str = price.show().ljust(num_chars)
    for c in range(num_chars):
      ch_one = pair_str[c]
      ch_two = price_str[c]
      # Display off
      lcd_byte(0x08, LCD_CMD)
      # Line one
      lcd_byte(0x80 | col, LCD_CMD)
      lcd_byte(ord(ch_one), LCD_CHR)
      # Line two
      lcd_byte(0xC0 | col, LCD_CMD)
      lcd_byte(ord(ch_two), LCD_CHR)
      # Scroll both lines
      lcd_byte(0x1B, LCD_CMD)
      # Display on
      lcd_byte(0x0C, LCD_CMD)
      # Mind the buffer
      #col = 0 if col >= 32 else col + 1
      col+=1
      if col > LCD_BUFFER:
        col=0
      # DEBUG
      print(" " + format(col, "2d") + " | 0x" + format(0x80 | col, "02X") + " | '" + ch_one + "' | 0x" + format(0xC0 | col, "02X") + " | '" + ch_two + "'")
      # Wait for keypress
      #if ord(readchar.readkey()) == 3:
      #  raise KeyboardInterrupt
      # Delay the scroll
      time.sleep(SCROLL_DELAY)
  # Return the active column, to be reused on subsequent calls
  return col

def main():
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

  # Custom font
  lcd_mkchars()

  prices = [
    Price("BTC","USD"),
    Price("BTC","EUR"),
#    Price("BTC","GBP"),
#    Price("BTC","JPY"),
#    Price("LTC","BTC"),
    Price("BTC","ETH"),
#    Price("BTC","XMR"),
#    Price("USD","DOGE"),
  ]

  timer = 0
  col = LCD_WIDTH

  while True:
    # Get prices
    if time.time() > (timer+API_RATE):
      # Clear the display
      lcd_byte(0x01, LCD_CMD)
      # Blinky cursor
      lcd_byte(0x0F, LCD_CMD)
      lcd_string("Getting", LCD_LINE_1)
      for price in prices:
        lcd_string("", LCD_LINE_2) # Clear
        lcd_string(price.pair(), LCD_LINE_2, False)
        price.update()
      timer = time.time()
      # Reset the starting column
      col = LCD_WIDTH
    # Show prices
    #prices_show(prices)
    col = prices_scroll(prices, col)

def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  #lcd_byte(0x22,LCD_CMD) # 100010 Initialise 4-bit mode
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
  GPIO.output(LCD_RS, mode)

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

def lcd_string(message,line,fill=True,fillchar=" "):
  # Cast to string
  message = str(message)
  # Send string to display
  if fill:
    message = message.ljust(LCD_WIDTH,fillchar)

  lcd_byte(line, LCD_CMD)

  for i in range(len(message)):
    lcd_byte(ord(message[i]),LCD_CHR)

def lcd_mkchars():
  # Custom chars (CGRAM)
  # 8 * (5x8)
  # Dollar (0x24) and Yen (0x5C) are in CGROM
  lcd_byte(0x40, LCD_CMD)
  chars = [
    0b00000,0b00100,0b01110,0b11111,0b00000,0b00000,0b00000,0b00000,# Up
    0b00000,0b00000,0b00000,0b11111,0b01110,0b00100,0b00000,0b00000,# Down
    0b01100,0b11110,0b01001,0b01110,0b01001,0b01001,0b11110,0b01100,# BTC
    0b00000,0b11111,0b00000,0b01110,0b00000,0b11111,0b00000,0b00000,# ETH
    0b01100,0b01010,0b01001,0b11101,0b01001,0b01010,0b01100,0b00000,# DOGE
    0b10001,0b11011,0b11111,0b10101,0b10001,0b10001,0b11011,0b00000,# XMR
    0b00110,0b01001,0b11100,0b01000,0b11100,0b01001,0b00110,0b00000,# EUR
    0b00110,0b01001,0b01000,0b11100,0b01000,0b01001,0b11111,0b00000,# GBP
    #0b01010,0b10101,0b01010,0b10101,0b01010,0b10101,0b01010,0b10101,# Dots
    #0b10101,0b01010,0b10101,0b01010,0b10101,0b01010,0b10101,0b01010,# Inverted Dots
    #0b11111,0b11011,0b10001,0b00000,0b11111,0b11111,0b11111,0b11111,# Inverted Up Arrow
    #0b11111,0b11111,0b11111,0b00000,0b10001,0b11011,0b11111,0b11111,# Inverted Down Arrow
  ]
  for b in chars:
    lcd_byte(b, LCD_CHR)
  lcd_byte(0x01, LCD_CMD)

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    #lcd_byte(0x01, LCD_CMD)
    #lcd_string("Goodbye!",LCD_LINE_1)
    GPIO.cleanup()
