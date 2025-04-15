from machine import Pin
import time

led = Pin(25, Pin.OUT)  # Onboard LED is on GPIO 25 (Pico only)

while True:
    led.toggle()
    time.sleep(0.5)
