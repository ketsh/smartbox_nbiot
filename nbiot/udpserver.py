from time import sleep_ms
from time import time as tm
from hashlib import sha256
import binascii, os
import vough_controller as vc

class UDPServer():
    def __init__(self, sim, display=None, wdt=None, led=None, keepAliveSec=120):
        self.sim = sim
        self.wdt = wdt
        self.display = display
        self.keepAliveSec = keepAliveSec
        self.led = led
        self.led.sign(5, typ="incoming")

    def open(self):
        try:
            while True:
                tryServerCnt = 1
                cr = self.sim.check("AT+CACID?", "CACID: 1")
                while  not cr:
                    cr = self.sim.openUDPServer()
                    sleep_ms(5000)
                    if tryServerCnt > 6:
                        break
                    tryServerCnt += 1
                timeout = self.keepAliveSec  # 2 min
                timeo = tm()
                cr = self.sim.check("AT+CACID?", "CACID: 1")
                while True and cr:
                    message = self.sim.udpIncomingMessage()
                    self.led.sign(times=1, typ="incoming")
                    self.wdt.feed()
                    try:
                        messageIdx = message.find("CARECV: ")
                        message = message[messageIdx + 8:]
                        msglen = message[0: message.find(",")]
                        message = message[message.find(",") + 1:]
                        messageDict = eval(message.replace("\r\n\r\nOK\r\n", ""))
                    except:
                        #print("invalid syntax")
                        pass

                    try:
                        command = messageDict["command"]
                        ret = self.sim.send(command, retType="o")
                        udp = self.sim.trySendUDPPackage(ret)
                        timeo = tm()
                    except:
                        #print("no Incoming command")
                        pass

                    try:
                        command = messageDict["open_locker"]
                        self.led.sign(times=2, typ="incoming")

                        board = int(command.split(",")[0])
                        door = int(command.split(",")[1])
                        controller = vc.VoungController()
                        controller.open_lock(board, door)
                        self.led.sign(1, typ="incoming")
                    except TypeError:
                        pass
                    except:
                        pass


                    try:
                        command = messageDict["frequency"]

                        f = open("frequency.cfg", "w")
                        f.write(str(command))
                        f.close()
                        hours = command
                    except TypeError:
                        #print("no frequency records")
                        pass
                    except:
                        #print("frequency error")
                        pass

                    try:
                        command = messageDict["get_logs"]

                        with open('esp32.log', 'r') as f:
                            lines = f.readlines()
                            last_two_lines = lines[-2:]
                        lines = ",".join(last_two_lines)
                        udp = self.sim.trySendUDPPackage(lines)
                        del lines, last_two_lines
                    except TypeError:
                        #print("no get_logs records")
                        pass
                    except:
                        #print("get_logs error")
                        pass

                    try:
                        command = messageDict["pycommand"]
                        ret = eval(command)
                        udp = self.sim.trySendUDPPackage(str(ret))
                    except TypeError:
                        #print("no pycommand records")
                        pass
                    except:
                        #print("pycommand error")
                        pass

                    try:
                        command = messageDict["fw"]
                        ret = command
                        start = ""
                        if "st" in ret.keys():
                            f = open("{}.fw".format(ret["fn"]), "w+b")
                            start = "start"
                        else:
                            f = open("{}.fw".format(ret["fn"]), "a+b")
                            start = "cont"
                        body = eval(ret["b"])
                        f.write(binascii.unhexlify(body))
                        f.close()
                        udp = self.sim.trySendUDPPackage("{} {} Done".format(ret["fn"], start))
                    except TypeError:
                        #print("no firmware records")
                        pass
                    except:
                        #print("firmware error")
                        pass

                    try:
                        command = messageDict["csum"]
                        csums = command
                        allOK = []
                        version = csums["v"]
                        for ret in csums["f"]:
                            s = sha256(open("{}.fw".format(ret["fn"]),'r+b').read()).digest()
                            hex_str = binascii.hexlify(s).decode('utf-8')
                            #print("hexlify checsum {}".format(hex_str))
                            if hex_str == ret["cs"]:
                                #print("checksum OK")
                                allOK.append({"old":"{}.fw".format(ret["fn"]), "new":ret["fn"]})
                        if len(allOK) == len(csums["f"]):
                            for fn in allOK:
                                os.rename(fn["old"], fn["new"])
                            udp = self.sim.trySendUDPPackage("Checksum Done")
                            f = open("version.cfg", "w+b")
                            f.write(version)
                            f.close()
                        else:
                            udp = self.sim.trySendUDPPackage("Checksum ERROR")
                    except TypeError:
                        #print("no checksum records")
                        pass
                    except Exception as e:
                        #print(e)
                        #print("checksum error")
                        pass
                    try:
                        command = messageDict["break"]
                        break
                    except:
                        #print("no break command")
                        pass

                    if timeout != None:
                        if (timeo + timeout < tm()):
                            break
                    #print("sleep")
                    sleep_ms(5000)
                    cr = self.sim.check("AT+CACID?", "CACID: 1")
                self.sim.send("AT+CACLOSE=1")
        except Exception as e:
            #print(e)
            pass
