from hx711_gpio import HX711
from time import sleep

class HX():
    def __init__(self, lcd, no=1):
        self.lcd = lcd
        self.hx711 = HX711(no)

    def measure(self):
        weight1 = self.hx711.read_average(times=20)
        self.lcd.show("Sulymeres..", clear=True)
        sleep(1)
        self.lcd.show("Sulymeres...", clear=False)
        sleep(1)
        self.lcd.show("Sulymeres....", clear=False)
        weight2 = self.hx711.read_average(times=20)
        self.lcd.show("Sulymeres.....", clear=False)
        weight = (weight1 + weight2) / 2
        self.lcd.status(2)
        weight = round((((weight-116882)/29.038)/1000),5)
        self.hx711.power_down()
        return weight
