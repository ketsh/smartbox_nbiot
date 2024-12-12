from machine import Pin
from time import sleep_ms

class LED():
    def __init__(self):
        self.r = Pin(2, Pin.OUT)
        self.g = Pin(5, Pin.OUT)
        self.b = Pin(18, Pin.OUT)

    def blink(self, color="g", ms=10):
        if color == "r":
            self.r.value(1)
            sleep_ms(ms)
            self.r.value(0)
        elif color=="b":
            self.b.value(1)
            sleep_ms(ms)
            self.b.value(0)
        else:
            self.g.value(1)
            sleep_ms(ms)
            self.g.value(0)

    def light(self, color="g"):
        if color == "r":
            self.r.value(1)
        elif color=="b":
            self.b.value(1)
        else:
            self.g.value(1)

    def off(self):
        self.r.value(0)
        self.b.value(0)
        self.g.value(0)
