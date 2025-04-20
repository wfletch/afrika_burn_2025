from machine import I2C, Pin
import time

# Constants
PCA9685_ADDR = 0x40
PCA9685_ADDR_2 = 0x41 
MODE1 = 0x00
PRESCALE = 0xFE
LED0_ON_L = 0x06



# RGB LED Class
class RGBLed:
    def __init__(self, host, pin_r, pin_g, pin_b):
        self.host = host
        self.r = pin_r 
        self.g = pin_g 
        self.b = pin_b 

    def set_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            raise ValueError('Hex color must be 6 characters long.')

        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        set_pwm(self.host, self.r, r/255 * 4095)
        set_pwm(self.host, self.g, g/255 * 4095)
        set_pwm(self.host, self.b, b/255 * 4095)

# Init I2C
i2c = I2C(0, scl=Pin(1), sda=Pin(0))

sleep_time_s = 0.03



# Wake and configure PCA9685
def init_pca9685(PCA_ADDR):
    i2c.writeto_mem(PCA_ADDR, MODE1, b'\x00')  # Normal mode
    time.sleep_ms(1)
    i2c.writeto_mem(PCA_ADDR, MODE1, b'\x10')  # Sleep
    prescale = int(25000000 / (4096 * 1000) - 1)   # 1000Hz
    i2c.writeto_mem(PCA_ADDR, PRESCALE, bytes([prescale]))
    i2c.writeto_mem(PCA_ADDR, MODE1, b'\x00')  # Wake
    time.sleep_ms(1)
    i2c.writeto_mem(PCA_ADDR, MODE1, b'\xa1')  # Auto-increment

def set_pwm(host, channel, value):
    value = int(value)
    reg = LED0_ON_L + 4 * channel
    data = bytes([0, 0, value & 0xFF, value >> 8])
    i2c.writeto_mem(host, reg, data)
init_pca9685(PCA_ADDR=PCA9685_ADDR)
init_pca9685(PCA_ADDR=PCA9685_ADDR_2)
# Breathing loop

def clear_all_channels():
    global sleep_time_s
    color = "#000000"
    for led_set in [rgb_leds_set_1, rgb_leds_set_2]:
        for led in led_set:
            led.set_rgb(color)
            time.sleep(sleep_time_s)

def trigger_switch_irq(pin : Pin):
    global sleep_time_s
    if pin.value() == 0:
        sleep_time_s = 0.3
    if pin.value() == 1:
        sleep_time_s = 0.03


rgb_leds_set_1 = [RGBLed(PCA9685_ADDR, i,i+1,i+2) for i in range(0,14,3)]    
rgb_leds_set_2 = [RGBLed(PCA9685_ADDR_2, i,i+1,i+2) for i in range(0,14,3)]    

trigger_switch_1= Pin(3, Pin.IN, Pin.PULL_DOWN)
trigger_switch_1.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=trigger_switch_irq)
clear_all_channels()
while True:
    for led_set in [rgb_leds_set_1, rgb_leds_set_2]:
        for led in led_set[0:2:1]:
            for color in ["#FF0000", "#00FF00", "#0000FF", "#000000"]:
                led.set_rgb(color)
                time.sleep(sleep_time_s)
