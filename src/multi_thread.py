import _thread
import time
from machine import Pin

# Initialize an LED (on Pico, the built-in LED is on GP25)
led = Pin(25, Pin.OUT)

# A lock to synchronize output (optional but good practice)
def test_thread():
    print_lock = _thread.allocate_lock()
    GLOBAL_KILL_ME = False
    GLOBAL_KILL_ME_ACK = False

    # Define a function to run on Core 1
    def core1_task():
        while True:
            # Use the lock to ensure prints don't intermix with the other core
            # print_lock.acquire()
            print("Core1: Blinking LED on core 1")
            # print_lock.release()
            led.toggle()              # toggle the LED state
            time.sleep(0.2)             # pause 1 second
            if GLOBAL_KILL_ME:
                print("breaking out of thread 1")
                GLOBAL_KILL_ME_ACK = True
                break

    # Launch the function on Core 1
    _thread.start_new_thread(core1_task, ())

    # Meanwhile, Core 0 continues with other work
    while True:
        # print_lock.acquire()
        try:
            print("Core0: Running on core 0")
            # print_lock.release()
            # (Core 0 could perform other tasks here, e.g. reading sensors)
            led.toggle()              # toggle the LED state
            time.sleep(0.2)               # pause 1.5 seconds
        except KeyboardInterrupt as KI:
            print("breaking out of thread 0")
            GLOBAL_KILL_ME = True
            break

    while True:
        if not GLOBAL_KILL_ME_ACK:
            print("Waiting for Global Kill Ack")
            break
        time.sleep(0.1)

