import machine
import neopixel
import time
import urandom

NUM_LEDS = 120
PIN = 5  # GPIO0
print("newo")

# Initialize NeoPixel strip
np = neopixel.NeoPixel(machine.Pin(PIN), NUM_LEDS)

# Set all LEDs to purple
for i in range(NUM_LEDS):
    np[i] = (255, 0, 255)  # RGB format
np.write()

# Animate: color wipe
time.sleep(5)
while True:
    brightness = urandom.getrandbits(8) / 256.0
    for i in range(NUM_LEDS):
        red = int(urandom.getrandbits(8) * brightness)
        # green = urandom.getrandbits(8) 
        green = int(255 * brightness) 
        blue = int(urandom.getrandbits(8) * brightness)
        np[i] = (
                red, green, blue
                )  

        np.write()
        time.sleep(0.01)

