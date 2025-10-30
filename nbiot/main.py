from sim7080 import SIM7080
import ssd1306
from smbus import SMBus
from machine import  Pin, SDCard, reset, UART, deepsleep, SoftI2C, WDT, RTC, WDT_RESET, reset_cause
from led import LED

from time import sleep_ms, sleep
from time import time as tm
import framebuf, math

from sht30 import SHT30
from hx711 import HX

from oled import OLED
import esp32
from utime import localtime, mktime

from qmp6988 import QMP6988
from udpserver import UDPServer
from esp32log import Log
from network import WLAN, STA_IF
from ubluetooth import BLE
from auxiliary import getBattery, reset_firmware_update, check_firmware_update, step_firmware_update,file_exists

def setupI2C():
    global  i2c
    #try:
    #    bus = smbus.SMBus(scl=Pin(22), sda=Pin(21))
    #except:
    #    bus = None
    i2c = SoftI2C(sda=Pin(21), scl=Pin(22))
    #i2c = I2C(0, sda=Pin(21), scl=Pin(22))

def getWakeupTime():
    current_time = rtc.datetime() # get the current time
    wake_up_time = None
    if current_time[4] >= hours[-1]:
        wake_up_time = mktime((current_time[0], current_time[1], current_time[2] + 1, hours[0], 0, 0, 0, 0, 0))
    else:
        for h in hours:
            if current_time[4] < h:
                wake_up_time = mktime((current_time[0], current_time[1], current_time[2], h, 0, 0, 0, 0, 0))
                break
    return wake_up_time

def goSleep(restartNeeded=False):
    global rtc
    deepsleep(10*1000)



class displaybulk():
    def __init__(self):
        pass

    def show(self, text, clear=True, line=1):
        pass

    def show2(self, text1, text2, clear=True):
        pass

    def status(self, iter=1):
        pass

    def clear(self):
        pass

    def on(self):
        pass

    def off(self):
        pass




if __name__=="__main__":
    try:
        while True:
            try:
                wifi = WLAN(STA_IF)
                wifi.active(False)
                bluetooth = BLE()
                bluetooth.active(False)
            except:
                pass
            led = LED()

            # 4 sign at startup and check colors
            led.sign(4)
            led.sign(4, typ="error")
            led.sign(4, typ="incoming")
            led.sign(4, typ="warning")


            rtc = RTC()

            sensorDict = {}
            if rtc.datetime()[0] < 2010:
                sensorDict["turn_on"] = 1
            log = Log(rtc)
            #log.log("Start up", "I", "w")
            log.log("Start up", "I", "a")
            #Wake Up Hours
            try:
                f = open("frequency.cfg", "r")
                freq = f.read()
                f.close()
                hours = eval(freq)
            except:
                hours = [2, 5, 7, 9, 11, 13, 15, 17, 19, 21]

            noDate = True


            ##init
            bus = None
            i2c = None
            setupI2C()
            lcd = displaybulk()
            log.log(reset_cause())

            wdt = WDT(timeout=60*60*1000)  # enable it with a timeout of 10min ---put it back
            wdt.feed()

            if reset_cause() == WDT_RESET:
                wdreset = True
                lcd.show("WDT Reset")
                try:
                    lcd.show("SIM CHECK")
                    sim = SIM7080(lcd, wdt, init=False, switch=False)
                    simAT = sim.checkRead("AT", "OK")
                    if simAT:
                        lcd.show("SIM OFF")
                        sim.sim_turned_on = True
                        sim.off()
                except:
                    lcd.show("SIM CHECK ERROR")
                    pass
                lcd.show("WDT Reset Starting")
                sleep_ms(1000)
                lcd.off()
                deepsleep(2*60*60*1000)
            else:
                wdreset = False

            try:
                version = "v{}".format(open("version.cfg", "r").readline())
            except:
                version = "v1.1"
            sensorDict["ver"] = version
            lcd.show(version)
            del version
            step_firmware_update()
            sleep_ms(500)
            ulp = esp32.ULP()
            ulp.set_wakeup_period(0, 1200*1000000)
            wdt.feed()


            try:
                led.sign(1, typ="warning")
                sim = SIM7080(lcd, wdt, led=led)
            except Exception as e:
                sleep(1)
                log.log("HIBA SIM: {}".format(str(e)), "E")

            if sim.atok:
                tryGetDate = 0
                while noDate and tryGetDate<=5:
                    try:
                        led.sign(1, typ="warning")
                        seconds_since_epoch = sim.getCLK()
                        if seconds_since_epoch != None:
                            lt = localtime(seconds_since_epoch)
                            rtc.init((lt[0], lt[1], lt[2], None, lt[3], lt[4], lt[5], 0))
                        noDate = False
                    except OverflowError:
                        sim.setNTPServer()
                        sleep_ms(500)
                    except Exception as e:
                        log.log("Date get error{}".format(str(e)), "E")
                    tryGetDate += 1

                current_time = rtc.datetime() # get the current time

                reset_firmware_update()
                udpServer = UDPServer(sim, lcd, wdt, led, keepAliveSec=None)
                udpServer.open()

            sim.enterPSMMode()
            sleep(10)
            goSleep(sim.getRestartNeeded())

    except Exception as e:
        log.log("Main Loop Error: {}".format(str(e)), "E")
        try:
            sim.off()
        except:
            pass
        goSleep(True)
