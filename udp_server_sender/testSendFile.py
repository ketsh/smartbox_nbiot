from sim7080 import SIM7080

from machine import Pin, SDCard, reset, UART, deepsleep, I2C, ADC, WDT, RTC
from time import sleep_ms
import time, sys
import esp32
from utime import localtime, mktime
from time import time as tm
import os

class WDTbulk():
    def __init__(self):
        pass

    def feed(self):
        pass

    def setupNBIOT(self):
        print("Setup NBIOT")
        self.show("Bekapcsolas...")
        self.atok = self.check('AT', 'OK')
        if self.atok:
            self.display.status(4)
            self.send('AT+CPSMS=0')
            self.send("AT+IPR=115200", False)
            self.check('AT+CPIN?', 'READY')
            self.display.status(5)
            self.send('AT+CPSMSTATUS=0', False)
            self.send(f'AT+CFUN=1,0')
            self.send('AT+CSQ', False)
            self.send('AT+CSCLK=0', False)
            self.send("AT+CFUN=1,0")
