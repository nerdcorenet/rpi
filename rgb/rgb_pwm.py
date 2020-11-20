#!/usr/bin/env python3

#### IMPORTS ####
import RPi.GPIO as GPIO
import time
import math


#### SETUP ####
PIN_R=14
PIN_G=15
PIN_B=18
PWM_FREQ=2000

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(PIN_R, GPIO.OUT)
GPIO.setup(PIN_G, GPIO.OUT)
GPIO.setup(PIN_B, GPIO.OUT)

r=GPIO.PWM(PIN_R, PWM_FREQ)
g=GPIO.PWM(PIN_G, PWM_FREQ)
b=GPIO.PWM(PIN_B, PWM_FREQ)

r.start(50)
b.start(50)
g.start(50)

#### MAIN ####
count = 0
while 1:
    s = math.sin(count)
    s2 = math.sin(count*2)
    s3 = math.sin(count*8)

    duty = (s + 1) * 50

    r.ChangeDutyCycle(duty)
    g.ChangeDutyCycle((s2 + 1)*50)
    b.ChangeDutyCycle((s3 + 1)*50)
    time.sleep(0.25)
    count = count + 1
