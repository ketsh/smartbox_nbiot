
from time import time, sleep_ms
from machine import UART, Pin
from utime import mktime
from re import search as rsearch
from auxiliary import file_exists

class SIM7080():
    print_ = False
    socketUDP = 0
    led = None
    restartNeeded = False
    display = None
    wdt = None
    def __init__(self, display=None, wdt=None, init=True, switch=True, led=None):
        #uart: SIM7020
        #self.uart2 = UART(2)
        self.simpwr = Pin(4, Pin.OUT)
        self.sim_turned_on = False
        self.atok = False
        self.totalSent = 0
        self.uart2 = UART(2, 19200,rx=16,tx=17,timeout=10)
        #self.uart2.init(115200, bits=8, parity=None, stop=1)
        self.display = display
        self.led = led
        self.wdt = wdt
        #self.off()
        self.led.sign(3, typ="warning")
        if switch:
            self.on()
        sleep_ms(10*1000)
        if init:
            sc = self.setupNBIOT()
            if not sc and self.atok:
                #self.off()
                #sleep_ms(13*1000)
                #self.on()
                self.restartNeeded = False
                #self.sendAdHoc("AT+CFUN=6")
                cr = self.checkRead("AT+CFUN=6", "PSUTTZ:", None, max_response_time=10)
                self.wdt.feed()
                sc = self.setupNBIOT()
        self.show("Initialized")

    def __del__(self):
        self.closeSocket()
        self.off()

    def getRestartNeeded(self):
        return self.restartNeeded

    def on(self):
        #turnon
        if not self.sim_turned_on:
            sleep_ms(1000)
            self.simpwr(0)
            sleep_ms(1000)
            self.simpwr(1)
            sleep_ms(1000)
            self.simpwr(0)
            sleep_ms(1000)
            #simpwr = Pin(4, Pin.IN)
            self.sim_turned_on = True

    def off(self):
        #turnoff
        if self.sim_turned_on:
            sleep_ms(2000)
            self.simpwr(1)
            sleep_ms(2000)
            self.simpwr(0)
            sleep_ms(2000)
            #simpwr = Pin(4, Pin.IN)
            self.sim_turned_on = False
    def show(self, text, cl=False):
        try:
            self.display.show(text, clear=cl)
        except:
            pass

    def setNTPServer(self):
        self.send('AT+CNTP="0.de.pool.ntp.org",0,0,0', retType="o")
        sleep_ms(500)
        self.send("AT+CNTP", retType="o")
        sleep_ms(500)
        self.send("AT+CNTP", retType="o")
        sleep_ms(500)

    def check(self, command, checkValue, sl_ms=500, timeout=10):
        timeo = time()
        while  True:

            initOK = self.send(command, retType="string", timeout=1)
            self.led.sign(1, typ="warning")
            sleep_ms(sl_ms-200)
            #self.wdt.feed()
            if initOK.find(checkValue) > -1:
                try:
                    self.show(f'{command} OK')
                except:
                    pass
                return True
            else:
                self.show(checkValue)
            if  (timeo + timeout < time()):
                return False

    def println(self, line):
        if self.print_:
            print(line)

    def setupNBIOT(self):
        self.println("Setup NBIOT")
        self.show("Bekapcsolas...", cl=True)
        self.atok = self.check('AT', 'OK', timeout=20)
        if self.atok:
            self.led.sign(3, typ="warning")
            self.display.status(4)
            self.send('AT+CPSMS=0')
            self.send("AT+IPR=19200", False)
            self.check('AT+CPIN?', 'READY')
            self.display.status(5)
            self.send('AT+CPSMSTATUS=0', False)
            self.send(f'AT+CFUN=1,0')
            self.send(f'AT+CNMP=38')
            self.send('AT+CSQ', retType="o")
            self.send('AT+CSCLK=0', False)
            self.send("AT+CLTS=1", retType="o")
            self.send("AT+CMNB=3", retType="o")
            ## check if attacked, return 1
            #self.send('AT+CREG=1')
            #self.sendAdHoc("AT+CREG?")
            cr = self.checkRead("AT+CREG?", "CREG:\s(\d+),([1|5])", retry_timeout=20, max_response_time=5)
            if not cr:
                self.send("AT+CREG=2")
                cr = self.checkRead("AT+CREG?", "CREG:\s(\d+),([1|5])", retry_timeout=120, max_response_time=5)

            self.createAPN()
            if not self.restartNeeded:
                cs = self.createSocket()
                return cs
        return False

    def checkRead(self, command, pattern, expected_value=None, retry_timeout=10, max_response_time=2):
        """
        Read from the UART and check if the received data matches the specified pattern.

        Parameters:
            pattern (str): Regular expression pattern to match against the received data.
            expected_value (int): Expected value to compare against the matched group (optional).
            timeout (float): Maximum time to wait for a matching response (in seconds).

        Returns:
            bool: True if the pattern is found within the specified timeout, False otherwise.
        """
        ret = False
        start_time_retry = time()
        while not ret:

            self.sendAdHoc(command)
            sleep_ms(100)

            start_time_wait = time()
            while True:

                try:
                    received_data = self.uart2.readline().decode()
                except Exception:
                    received_data = ''

                rs = rsearch(pattern, received_data)

                if rs:
                    if expected_value is not None:
                        matched_value = int(rs.group(1))
                        if matched_value == expected_value:
                            ret = True
                        else:
                            ret = False
                    else:
                        ret = True
                    break

                if time() > start_time_wait + max_response_time:
                    # Log or self.println a message indicating that the timeout has occurred
                    break
            if time() > start_time_retry + max(max_response_time, retry_timeout):
                # Log or self.println a message indicating that the timeout has occurred
                break
        return ret

    def openUDPServer(self):
        self.send('AT+CACLOSE=1')
        self.led.sign(1, typ="warning")
        cr = self.send('AT+CACID=1')
        cr = self.check('AT+CACID?', 'CACID: 1')
        self.led.sign(1, typ="warning")
        if cr:
            cr = self.send('AT+CASERVER=1,0,"UDP",6005')
        return  cr

    def udpIncomingMessage(self):
        self.led.sign(1, typ="warning")
        cr = self.send('AT+CARECV=1,512', retType="o")
        return cr

    def trySendUDPPackage(self, recv):
        udptry = 1
        udp = False
        while not udp:
            udp = self.sendUDPPackage(recv)

            if udp:
                break

            if udptry < 3:
                sleep_ms(1000)
                break
            udptry += 1
        return udp

    def signalCheck(self):
        ss = False
        try:
            ret = self.send('AT+CSQ', retType='o')
            rs = rsearch("CSQ:\s([1-9]\d*),\d+", ret)
            signal = int(rs.group(1))
            if signal > 2:
                ss = True
        except:
            pass
        return ss

    def sendUDPPackage(self, recv):
        lenRecv = len(recv)
        self.sendAdHoc(f'AT+CASEND={self.socketUDP},{lenRecv}')
        sleep_ms(10)
        #self.sendAdHoc(recv)
        cr = self.checkRead(recv, "OK")
        sleep_ms(100)
        if cr:
            #self.sendAdHoc(f'AT+CAACK=0')
            sleep_ms(10)
            self.println("SendUDP LEN: {}".format(lenRecv))
            ack = self.checkRead(f'AT+CAACK=0', "ACK:\s([1-9]\d*),\d+", lenRecv)
            #self.println("debug 4")
            return  ack
        else:
            return False

    def sendAdHoc(self, command):
        self.uart2.write(bytearray(command+"\r\n"))

    def send(self, command, waitStatus=True, retType="bool", timeout=5):
        for r in range(0,10):
            self.uart2.read()
        self.uart2.write(bytearray(command+"\r\n"))

        outputtext = ''
        atLeastOne = False
        timeo = time()
        while True:
            try:
                k = (self.uart2.readline()).decode()
                atLeastOne = True
            except Exception as e:
                k = ''
            outputtext = (str(outputtext) + str(k))
            #self.wdt.feed()
            if (atLeastOne and (not waitStatus or k.strip() in ['OK', 'ERROR'])) or (timeo + timeout < time()):
                break
        self.println("-----SENDING-----")
        self.println(outputtext)
        self.println("---SENDING END---")
        if retType == "bool":
            if k.strip() == "ERROR":
                self.show("Hiba: {}".format(command))
                return False
            else:
                return True
        else:
            return outputtext

    def CSOC(self):
        ot = self.send("AT+CACID=0", True, "output")
        #self.sendAdHoc('AT+CAOPEN=0,0,"UDP","udp.os.1nce.com",4445,0')
        cr = self.checkRead('AT+CAOPEN=0,0,"UDP","udp.os.1nce.com",4445,0', "CAOPEN: 0,0")
        if cr:
            return 0
        else:
            self.restartNeeded = True
            return None

    def getSocketNo(self):
        self.println("Creating socket")
        for si in range(0, 5):
            ot = self.send(f'AT+CAOPEN?', True, "output")
            if ot.find("0,0") > -1:
                self.show("Kapcsolat indit")
                return 0
        return None

    def createAPN(self):
        self.println("Creating APN")
        self.show("APN beallitas")
        #self.tryWrite(f'AT+CSOCON={self.socketUDP},4445,10.60.2.239')
        self.send('AT+CACFG="KEEPALIVE",0', retType="o")
        cr = self.check('AT+CGCONTRDP', "iot.1nce.net")
        if not cr:
            self.send('AT+CNCFG=0,1,"iot.1nce.net","","",0')
            self.send('AT+CGDCONT=1,"IP","iot.1nce.net"')
        #self.send('AT+CGPADDR', retType="output")

        #self.send('AT+CNACT=0,1', retType="string")

        cnact = self.check("AT+CNACT?", "CNACT: 0,1", timeout=10)
        if not cnact:
            self.send('AT+CNACT=0,1', retType="string")
            cnact = self.check("AT+CNACT?", "CNACT: 0,1", timeout=10)
            restartNeeded = not cnact
        self.display.status(6)
        cr = self.check("AT+CGATT?", "CGATT: 1")
        if not cr:
            self.send("AT+CREG=2")
            self.send("AT+CGREG=1")
            self.send("AT+CEREG=1")
            self.check("AT+CGATT=1", "CGATT: 1", sl_ms=80000, timeout=80)
            cr = self.check("AT+CGATT?", "CGATT: 1")
            restartNeeded = not cr

        self.send('AT+COPS?', retType="string")

        ## IP Aplication
        #self.send('AT+CNACT?', retType="string")
        self.display.status(7)
        if cr:
            self.show("APN letrejott")
        else:
            self.show("APN nem OK")

    def createSocket(self):
        self.socketUDP = self.getSocketNo()
        wi = 0
        while self.socketUDP == None and wi < 3:
            self.println("Opening socket")
            self.show("Socket indit")
            self.socketUDP = self.CSOC()
            #self.wdt.feed()
            wi += 1
            if self.socketUDP == None:
                self.closeSocket()
        if self.socketUDP == None:
            self.println(f'Socket Hiba')
            self.show("Socket Hiba")
            self.display.status(8)
            return False
        else:
            self.println(f'Socket created: {self.socketUDP}')
            self.show("Socket OK")
            self.restartNeeded = False
            return True

    def closeSocket(self):
        #Close UPD
        self.send('AT+CACLOSE=0', retType="string")
        self.show("Socket bontas")
        #self.send(f'AT+CFUN=0,0')
        #self.send(f'AT+CSCLK=2')

    def enterPSMMode(self):
        #self.show("Retention")
        #self.send('AT+RETENTION=0')
        #self.show("Cereg")
        try:
            self.send('AT+CGNSPWR=0', retType="string")
            self.send('AT+CEREG=4')
            #if not self.signalCheck():

            cr = self.check("AT+CPSI?", "LTE NB-IOT", sl_ms=100, timeout=3)
            if not cr or not self.checkPSMMode() or file_exists("fnc_psmMode_always.cfg"):
                self.off()
            else:
                self.send('AT+CPSMSTATUS=1')
                #self.show("CPSMSTATUS")
                self.send(f'AT+CPSMS=1,,,"01010100","00010000"')
        except:
            self.off()

        #TODO: check if there is a signal strength, if not, then turn off

        #self.check('AT+CPSMS=1,,,"00100010","00000001"', "CPSMS: 1", 5000)
        #+CEREG: 4,5,"C350","0001766A",9,"00",,,"00000001","00001100" 10m, 2*12sec = 24sec active

    def gps(self):
        self.send('AT+CGNSWARM', retType="string")
        self.send('AT+CGNSPWR=1', retType="string")

        sleep_ms(5000)
        try:
            lat = "0.000000"
            long = "0.000000"
            for n in range(8):
                gps = self.send("AT+CGNSINF", retType="o")
                gpsidx = gps.find("CGNSINF: ")+9
                gps = gps[gpsidx:].split(",")
                lat = gps[3]
                long = gps[4]
                if lat != "0.000000" and lat != None and lat != "":
                    break
                sleep_ms(10000)
            return (lat, long)
        except:
            self.send('AT+CGNSPWR=0', retType="string")
            return ("", "")

    def closeGps(self):
        self.send('AT+CGNSPWR=0', retType="string")

    def checkPSMMode(self):
        #self.sendAdHoc("AT+COPS?")
        psm_enable = self.checkRead("AT+COPS?", r'\+COPS: \d+,\d+,"[^"]+",(\d+)', 9, max_response_time=45)
        #return self.checkRead("ENTER PSM")
        return psm_enable

    def getCLK(self):
        try:
            clk = self.send("AT+CCLK?", retType="o")
            clkidx = clk.find("CCLK:")+7
            rtc_datetime = clk[clkidx:clkidx+20]
            year = int(rtc_datetime[0:2])
            month = int(rtc_datetime[3:5])
            day = int(rtc_datetime[6:8])
            hour = int(rtc_datetime[9:11])
            minute = int(rtc_datetime[12:14])
            second = int(rtc_datetime[15:17])
            timezone_hour = int(rtc_datetime[18:20])
            seconds_since_epoch = mktime((2000+year, month, day, hour, minute, second, timezone_hour, 0))
            return seconds_since_epoch
        except:
            return None

