from machine import Pin
from time import sleep_ms


class LED:
    def __init__(self):
        self.r = Pin(2, Pin.OUT)
        self.g = Pin(5, Pin.OUT)
        self.b = Pin(18, Pin.OUT)

    def blink(self, color="g", ms=10):
        # Turn off all LEDs first to ensure a clean state
        self.off()

        # Turn on the appropriate LED(s) based on color
        if color == "r":
            self.r.value(1)
        elif color == "b":
            self.b.value(1)
        elif color == "y":  # Yellow: turn on red and green
            self.r.value(1)
            self.g.value(1)
        else:  # Default to green
            self.g.value(1)

        sleep_ms(ms)
        self.off()  # Turn off all LEDs after the duration

    def light(self, color="g"):
        # Turn off all LEDs first to ensure only the desired color is on
        self.off()

        # Turn on the appropriate LED(s) based on color
        if color == "r":
            self.r.value(1)
        elif color == "b":
            self.b.value(1)
        elif color == "y":  # Yellow: turn on red and green
            self.r.value(1)
            self.g.value(1)
        else:  # Default to green
            self.g.value(1)

    def off(self):
        self.r.value(0)
        self.g.value(0)
        self.b.value(0)

    def sign(self, times=1, typ="info"):
        color = "g"
        if typ == "error":
            color = "r"
        elif typ == "incoming":
            color = "b"
        elif typ == "warning":  # Add yellow for warning
            color = "y"

        for _ in range(times):
            self.blink(color, ms=200)  # Use the blink method with 200ms duration
            sleep_ms(200)