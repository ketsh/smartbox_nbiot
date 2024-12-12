from time import sleep
import ssd1306
from json import load as json_load

class OLED():
    display = None
    def __init__(self, i2c=None):
        self.display = ssd1306.SSD1306_I2C(128, 32, i2c)
        self.on()

    def show(self, text, clear=True, line=1):
        if clear:
            self.clear()
        else:
            self.display.fill_rect(0, 0, 128, 15, 0)
        if line==1:
            self.display.text(text, 0, 0, 1)
        else:
            self.display.text(text, 0, 30, 1)
        self.display.show()

    def show2(self, text1, text2, clear=True):
        if clear:
            self.clear()

        self.display.text(text1, 0, 0, 1)
        self.display.text(text2, 0, 15, 1)
        self.display.show()

    def status(self, iter=1):
        for r in range(iter):
            self.display.fill_rect(20+((r-1)*10),15,8,15, 1)
        self.display.show()

    def clear(self):
        self.display.fill(0)
        self.display.show()

    def on(self):
            self.display.poweron()

    def off(self):
            self.display.poweroff()


    def showBigText(self, text):
        with open('pixel_dict_kg.json', "r") as json_file:
            pixels_ok = json_load(json_file)
        idx = 0
        self.clear()
        for t in list(text):
            try:
                for pixel in pixels_ok[t]:
                    self.display.pixel(pixel[0]+idx*20+5, pixel[1], 1)
            except:
                pass
            idx += 1
        self.display.show()
