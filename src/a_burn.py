from machine import I2C, Pin
import neopixel
import urandom
import math
import time

# PCA9685 Constants
MODE1 = 0x00
PRESCALE = 0xFE
LED0_ON_L = 0x06

PCA9685_ADDR_1 =  0x40
PCA9685_ADDR_2 =  0x41
PCA9685_ADDR_3 =  0x42
PCA9685_ADDR_4 =  0x43

# Neopixel Constants
NEOPIXEL_REGION_1_PIN = 5
NEOPIXEL_REGION_1_NUM_LEDS = 32
NEOPIXEL_REGION_2_PIN = 6
NEOPIXEL_REGION_2_NUM_LEDS = 16 
NEOPIXEL_REGION_3_PIN = 7
NEOPIXEL_REGION_3_NUM_LEDS = 32
# I2C Constants
I2C_CHANNEL_1_SCL_PIN = 1
I2C_CHANNEL_1_SDA_PIN = 0
i2c = I2C(0, scl=Pin(I2C_CHANNEL_1_SCL_PIN), sda=Pin(I2C_CHANNEL_1_SDA_PIN))
# Missle Switches
MISSLE_SWITCH_1_PIN = 3
MISSLE_SWITCH_2_PIN = 4

# Logical 
ACTIVE_PATTERN = 0
SLEEP_TIME_MS = 1000 
CUR_CYCLE_COUNT = 0
GLOBAL_COLOR = "#FF0000"
class PCA9685():
    def __init__(self, i2c_device, addr):
        self.i2c =  i2c_device
        self.addr = addr
        self.i2c.writeto_mem(self.addr, MODE1, b'\x00')  # Normal mode
        time.sleep_ms(1)
        self.i2c.writeto_mem(self.addr, MODE1, b'\x10')  # Sleep
        prescale = int(25000000 / (4096 * 1000) - 1)   # 1000Hz
        self.i2c.writeto_mem(self.addr, PRESCALE, bytes([prescale]))
        self.i2c.writeto_mem(self.addr, MODE1, b'\x00')  # Wake
        time.sleep_ms(1)
        self.i2c.writeto_mem(self.addr, MODE1, b'\xa1')  # Auto-increment

    def set_pwm(self, channel, value):
        value = int(value)
        reg = LED0_ON_L + 4 * channel
        data = bytes([0, 0, value & 0xFF, value >> 8])
        self.i2c.writeto_mem(self.addr, reg, data)
        

class RGBLed:
    def __init__(self, pca_9685, pin_r, pin_g, pin_b):
        self.host = pca_9685
        self.r = pin_r 
        self.g = pin_g 
        self.b = pin_b 

    def turn_off(self):
        self.set_rgba("#000000", 0)
    def set_rgba(self, hex_color, brightness=1):
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            print(hex_color)
            raise ValueError('Hex color must be 6 characters long.')

        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        self.host.set_pwm(self.r, r/255 * 4095 * brightness)
        self.host.set_pwm(self.g, g/255 * 4095 * brightness)
        self.host.set_pwm(self.b, b/255 * 4095 * brightness)




# Initialize NeoPixel strip
class NeoPixelStrip():
    def __init__(self, pin_number, LED_count):
        self.pin_number = pin_number
        self.LED_count = LED_count
        self.np : neopixel.NeoPixel = neopixel.NeoPixel(Pin(self.pin_number), self.LED_count)

    def set_debug_mode(self):
        # Set all LEDs to purple
        for i in range(self.LED_count):
            self.np[i] = (0xFF, 0xB6, 0xC1)  # RGB format
        self.np.write()

    def color_lin_grad(self, offset=0, color="#FF0000"):
        color = color.lstrip("#")
        colors = [color[0:2], color[2:4], color[4:6]]
        colors = [int(colors[i], 16) for i in range(len(colors))]
        brightness_delta = 1/self.LED_count
        for i in range(self.LED_count):
            self.np[i] = (
                            int(colors[0] * ((i + offset)%self.LED_count)*brightness_delta), 
                            int(colors[1] * ((i + offset)%self.LED_count)*brightness_delta), 
                            int(colors[2] * ((i + offset)%self.LED_count)*brightness_delta), 
                            )
        self.np.write()





neopixel_region_1 = NeoPixelStrip(NEOPIXEL_REGION_1_PIN, NEOPIXEL_REGION_1_NUM_LEDS)
neopixel_region_2 = NeoPixelStrip(NEOPIXEL_REGION_2_PIN, NEOPIXEL_REGION_2_NUM_LEDS)
neopixel_region_3 = NeoPixelStrip(NEOPIXEL_REGION_3_PIN, NEOPIXEL_REGION_3_NUM_LEDS)

all_neopixel = [neopixel_region_1, neopixel_region_2, neopixel_region_3]

for n in all_neopixel:
    n.set_debug_mode()

def trigger_switch_irq_missle_1(pin : Pin):
    global SLEEP_TIME_MS
    if pin.value() == 0:
        SLEEP_TIME_MS = 100 
    if pin.value() == 1:
        SLEEP_TIME_MS = 1000

def trigger_switch_irq_missle_2(pin : Pin):
    global GLOBAL_COLOR 
    if pin.value() == 0:
        GLOBAL_COLOR = "#00FF00"
    if pin.value() == 1:
        rand_r = hex(urandom.getrandbits(8))[2::]
        rand_g = hex(urandom.getrandbits(8))[2::]
        rand_b = hex(urandom.getrandbits(8))[2::]
        GLOBAL_COLOR = f"#{rand_r}{rand_g}{rand_b}"

trigger_switch_1 = Pin(MISSLE_SWITCH_1_PIN, Pin.IN, Pin.PULL_DOWN)
trigger_switch_1.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=trigger_switch_irq_missle_1)
trigger_switch_2 = Pin(MISSLE_SWITCH_2_PIN, Pin.IN, Pin.PULL_DOWN)
trigger_switch_2.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=trigger_switch_irq_missle_2)

# Main Color Loop

while True:  
    neopixel_region_1.color_lin_grad(color=GLOBAL_COLOR,offset=CUR_CYCLE_COUNT);
    CUR_CYCLE_COUNT+=1
    time.sleep_ms(SLEEP_TIME_MS)
