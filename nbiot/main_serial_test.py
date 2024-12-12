# Write your code here :-)
from time import sleep_ms
from time import time as tm
from hashlib import sha256
import binascii, os
import vough_controller as vc

from led import LED

if __name__=="__main__":
    try:
        controller = vc.VoungController()
        led = LED()

        while True:
            try:
                controller.open_lock(0, 11)
                sleep_ms(3000)
                led.blink()
            except:
                sleep_ms(100)
                led.blink()
                sleep_ms(100)
                led.blink()
                sleep_ms(100)
                led.blink()
                sleep_ms(3000)
                controller.open_lock(0, 11, byt = False)
                sleep_ms(3000)
    except:
        sleep_ms(100)
        led.blink()
        sleep_ms(100)
        led.blink()
        sleep_ms(100)
        led.blink()
        sleep_ms(100)
        led.blink()
        sleep_ms(100)
        led.blink()

