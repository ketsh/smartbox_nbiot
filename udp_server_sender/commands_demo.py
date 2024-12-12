import binascii
import socket
from time import sleep
UDP_IP_ADDRESS = "10.181.161.2" #8988228066602756535
UDP_IP_ADDRESS = "10.181.161.111" #8988228066603096577
UDP_IP_ADDRESS = "10.181.161.107" #8988228066602756535
UDP_IP_ADDRESS = "10.181.161.214"
UDP_PORT_NUMBER = 6005
#MESSAGE = """{"command": "AT+CSQ", "break": True, "frequency": [5, 10, 15, 20], "get_logs": True, "pycommand": 'sim.send("AT", retType="o")'}"""
MESSAGE = """{"command": "AT+CSQ", "frequency": [8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20], "get_logs": True}"""

#Getting signal strength
MESSAGE = """{"command": "AT+CSQ"}"""

#List directory
MESSAGE = """{"pycommand": "os.dirlist()"}"""

#Getting last entry of esp32log
MESSAGE = """{"pycommand": "[i for i in open('esp32.log', 'r+')][10]"}"""

#drop esp32.log
MESSAGE = """{"pycommand": "os.remove('esp32.log)"}"""

#break udpserver
MESSAGE = """{"break": True}"""

##GPS
MESSAGE = """sim.send('AT+CGNSPWR=1', retType="string")"""
MESSAGE = """sim.send("AT+CGNSINF", retType="o")"""


client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.sendto(MESSAGE.encode(), (UDP_IP_ADDRESS, UDP_PORT_NUMBER))
client_socket.close()



#sending files

import os, hashlib
os.chdir("km/udp_server_sender")
sendFiles = ["testSendFile.py"]

os.chdir("km")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sendFiles = ["main.py"]

def sendFile():
    global sendFiles, client_socket
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
                client_socket.sendto(MESSAGE.encode(), (UDP_IP_ADDRESS, UDP_PORT_NUMBER))
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
    global sendFiles, client_socket
    checksumList = []
    for fn in sendFiles:
        cs  = hashlib.sha256(open(fn,'rb').read()).hexdigest()
        checksumList.append({"fn": fn, "cs":cs})
    MESSAGE = """{{"csum": {{"v": 1.2x, "f": {}}}}}""".format(checksumList)
    client_socket.sendto(MESSAGE.encode(), (UDP_IP_ADDRESS, UDP_PORT_NUMBER))



## BREAK
MESSAGE = """{"break": True}"""
client_socket.sendto(MESSAGE.encode(), (UDP_IP_ADDRESS, UDP_PORT_NUMBER))


MESSAGE = """{"command": "AT+CSQ"}"""
client_socket.sendto(MESSAGE.encode(), (UDP_IP_ADDRESS, UDP_PORT_NUMBER))
