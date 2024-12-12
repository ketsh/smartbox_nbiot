import binascii
import socket
from time import sleep
import os, hashlib

class UDPSender():
    def __init__(self):
        self.client_socket = None
        self.UDP_IP_ADDRESS = None
        self.UDP_PORT_NUMBER = None
        self.DEVICE_ICCID = None
    def open(self, DEVICE_ICCID):
        self.DEVICE_ICCID = DEVICE_ICCID
        device_map = {
            "8988228066602756535":"10.181.161.2",
            "8988228066603096577": "10.181.161.111",
            "8988228066603096578": "10.181.161.107",
            "8988228066603096579": "10.181.161.214",
            "8988228066603096580": "10.181.161.3",
            "8988228066603096581": "10.181.161.233",
            "8988228066603096583": "10.181.161.5",
        }
        self.UDP_IP_ADDRESS = device_map[DEVICE_ICCID]
        self.UDP_PORT_NUMBER = 6005

        try:
            self.client_socket.close()
        except:
            pass
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def getCurrentDevice(self):
        return self.DEVICE_ICCID
    def send(self, command, inputvar=None):
        if command == "Get Signal strength":
            MESSAGE = """{"command": "AT+CSQ"}"""
        elif command == "Get Clock":
            MESSAGE = """{"command": "AT+CCLK?"}"""
        elif command == "Get Frequency":
            MESSAGE = """{"pycommand": "open('frequency.cfg', 'r+b').readline()"}"""
        elif command == "Break":
            MESSAGE = """{"break": True}"""
        elif command == "Set High Frequency":
            MESSAGE = """{"frequency": [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21]}"""
        elif command == "Set Medium Frequency":
            MESSAGE = """{"frequency": [5, 7, 9, 11, 13, 16, 18, 20]}"""
        elif command == "Set Low Frequency":
            MESSAGE = """{"frequency": [13, 22]}"""
        elif command == "Get Version":
            MESSAGE = """{"pycommand": "open('version.cfg', 'r+b').readline()"}"""
        elif command == "Read ESP32 Log":
            MESSAGE = """{{"pycommand": "[i for i in open('esp32.log', 'r+')][{}]"}}""".format(inputvar)
        elif command == "Read ESP32 Last 10":
            MESSAGE = """{{"pycommand": "[i for i in open('esp32.log', 'r+')][-10:]"}}"""
        elif command == "Open Door":
            MESSAGE = """{{"open_locker": "{}"}}""".format(inputvar)
        print (MESSAGE)
        self.client_socket.sendto(MESSAGE.encode(), (self.UDP_IP_ADDRESS, self.UDP_PORT_NUMBER))

    def close(self):
        self.client_socket.close()


    def sendFile(self):

        os.chdir("km/udp_server_sender")
        sendFiles = ["testSendFile.py"]

        os.chdir("km")
        sendFiles = ["main.py"]

        def sendFile():
            for fn in sendFiles:
                start = True
                with open(fn, "r+b") as f:
                    while True:
                        content = f.read(200)
                        if not content:
                            break
                        if start:
                            testc = str(content)
                            package = """{{"fw": {{"st": True, "fn":"{}", "b":"{}"}}}}""".format(fn, binascii.hexlify(content))
                        else:
                            package = """{{"fw": {{"fn":"{}", "b":"{}"}}}}""".format(fn, binascii.hexlify(content))
                        print(len(package))
                        #print(eval(package))
                        start = False
                        MESSAGE = package
                        self.client_socket.sendto(MESSAGE.encode(), (self.UDP_IP_ADDRESS, self.UDP_PORT_NUMBER))
                        sleep(15)

        sendFile(sendFiles)


        #sending checksum
        """
         dict
            v: string - version number
            f: array< dict <string, string>> - filenames
                fn - filename
                cs - checksum
        """

        ### Calculating checksum
        # Approx we can send 3 files in a checksum batch, as the checksum size for 1 file is ~100bytes

        def checkChecksum():

            checksumList = []
            for fn in sendFiles:
                cs  = hashlib.sha256(open(fn,'rb').read()).hexdigest()
                checksumList.append({"fn": fn, "cs":cs})
            MESSAGE = """{{"csum": {{"v": 1.2x, "f": {}}}}}""".format(checksumList)
            self.client_socket.sendto(MESSAGE.encode(), (self.UDP_IP_ADDRESS, self.UDP_PORT_NUMBER))



        ## BREAK
        MESSAGE = """{"break": True}"""
        self.client_socket.sendto(MESSAGE.encode(), (self.UDP_IP_ADDRESS, self.UDP_PORT_NUMBER))


