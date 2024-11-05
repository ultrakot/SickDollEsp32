from machine import Pin
from time import sleep_ms

led = Pin(15, Pin.OUT)
led.on()
while True:
  led.on()
  sleep_ms(100)
  led.off()
  sleep_ms(100)